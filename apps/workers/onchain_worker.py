# apps/workers/onchain_worker.py
import asyncio
import json
import sys
import os
from datetime import datetime
from decimal import Decimal
from typing import Set, Optional, Dict, Any
import uuid

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv
import websockets
from web3 import Web3
import structlog

load_dotenv()

from packages.database.engine import AsyncSessionLocal
from packages.database.models.whale_transaction import WhaleTransaction

logger = structlog.get_logger()

class OnchainWorker:
    def __init__(self):
        self.alchemy_key = os.getenv("ALCHEMY_API_KEY")
        if not self.alchemy_key:
            raise ValueError("ALCHEMY_API_KEY not found in environment")
        
        self.ws_url = f"wss://eth-mainnet.g.alchemy.com/v2/{self.alchemy_key}"
        self.http_url = f"https://eth-mainnet.g.alchemy.com/v2/{self.alchemy_key}"
        
        # Initialize Web3 for block queries
        self.web3 = Web3(Web3.HTTPProvider(self.http_url))
        
        # Known exchange addresses to filter out
        self.known_exchanges = {
            "0x28C6c06298d514Db089934071355E5743bf21d60",  # Binance 14
            "0x9696f59E4d72E237BE84fFD425DCaD154Bf96976",  # Coinbase 5
            "0x6cc5f688a315f3dc28a7781717a9a798a59fda7b",  # OKX
        }
        
        # Whale thresholds (realistic values for actual whales)
        self.whale_threshold_high = Decimal("500")   # ETH 
        self.whale_threshold_normal = Decimal("200") # ETH 
        
        self.running = False
        self.websocket = None
    
    async def connect_websocket(self):
        """Connect to Alchemy WebSocket and subscribe to new blocks"""
        try:
            logger.info("Connecting to Alchemy WebSocket")
            self.websocket = await websockets.connect(self.ws_url)
            
            # Subscribe to new block headers
            subscription = {
                "id": 1,
                "method": "eth_subscribe",
                "params": ["newHeads"]
            }
            
            await self.websocket.send(json.dumps(subscription))
            logger.info("Subscribed to new blocks")
            
            return True
            
        except Exception as e:
            logger.error("Failed to connect to WebSocket", error=str(e))
            return False
    
    async def process_block(self, block_number: int):
        """Process a single block for whale transactions"""
        try:
            logger.info(f"Processing block {block_number}")
            
            # Get full block with transactions
            block = self.web3.eth.get_block(block_number, full_transactions=True)
            
            whale_count = 0
            for tx in block.transactions:
                if await self.analyze_transaction(tx, block.timestamp):
                    whale_count += 1
            
            if whale_count > 0:
                logger.info(f"Found {whale_count} whale transactions in block {block_number}")
                
        except Exception as e:
            logger.error(f"Error processing block {block_number}", error=str(e))
    
    async def analyze_transaction(self, tx, block_timestamp: int) -> bool:
        """Analyze transaction to determine if it's a whale transfer"""
        try:
            # Convert wei to ETH
            value_eth = Decimal(tx.value) / Decimal(10**18)
            
            # Skip if below minimum threshold
            if value_eth < self.whale_threshold_normal:
                return False
            
            # Skip if from/to is None (contract creation)
            if not tx['from'] or not tx['to']:
                return False
            
            from_address = tx['from']
            to_address = tx['to']
            
            # Check if exchange is involved
            exchange_involved = (
                from_address in self.known_exchanges or 
                to_address in self.known_exchanges
            )
            
            # Determine priority level
            priority_level = "high" if value_eth >= self.whale_threshold_high else "normal"
            
            # Estimate USD value (simplified - using ~$1800/ETH)
            value_usd = value_eth * Decimal("1800")
            
            # Save to database
            await self.save_whale_transaction({
                "tx_hash": tx.hash.hex(),
                "block_number": tx.blockNumber,
                "timestamp": datetime.fromtimestamp(block_timestamp),
                "from_address": from_address,
                "to_address": to_address,
                "value_eth": value_eth,
                "value_usd": value_usd,
                "gas_used": tx.gas,
                "gas_price": tx.gasPrice,
                "priority_level": priority_level,
                "exchange_involved": exchange_involved,
                "ingest_id": str(uuid.uuid4()),
                "source": "alchemy"
            })
            
            logger.info(f"Whale detected: {value_eth} ETH ({priority_level} priority)")
            return True
            
        except Exception as e:
            logger.error("Error analyzing transaction", error=str(e))
            return False
    
    async def save_whale_transaction(self, whale_data: Dict[str, Any]):
        """Save whale transaction to database"""
        try:
            async with AsyncSessionLocal() as session:
                # Check if transaction already exists by tx_hash
                from sqlalchemy import select
                stmt = select(WhaleTransaction).where(WhaleTransaction.tx_hash == whale_data["tx_hash"])
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()
                
                if existing:
                    logger.info(f"Transaction already exists: {whale_data['tx_hash'][:10]}...")
                    return  # Skip duplicates
                
                whale_tx = WhaleTransaction(**whale_data)
                session.add(whale_tx)
                await session.commit()
                
                logger.info(f"✅ Saved whale transaction to DB: {whale_data['tx_hash'][:10]}... ({whale_data['value_eth']} ETH)")
                
        except Exception as e:
            logger.error("❌ Error saving whale transaction", error=str(e))
    
    async def listen_for_blocks(self):
        """Listen for new blocks from WebSocket"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                
                if "method" in data and data["method"] == "eth_subscription":
                    # New block notification
                    block_data = data["params"]["result"]
                    block_number = int(block_data["number"], 16)
                    
                    # Process block in background
                    asyncio.create_task(self.process_block(block_number))
                    
                elif "id" in data and data["id"] == 1:
                    # Subscription confirmation
                    logger.info(f"Subscription confirmed: {data.get('result')}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
        except Exception as e:
            logger.error("Error in WebSocket listener", error=str(e))
    
    async def run(self):
        """Main worker loop"""
        self.running = True
        logger.info("Starting onchain worker")
        
        while self.running:
            try:
                # Connect to WebSocket
                if await self.connect_websocket():
                    # Listen for new blocks
                    await self.listen_for_blocks()
                
                # If we get here, connection was lost
                logger.warning("Connection lost, reconnecting in 5 seconds...")
                await asyncio.sleep(5)
                
            except KeyboardInterrupt:
                logger.info("Shutdown requested")
                self.running = False
            except Exception as e:
                logger.error("Unexpected error in main loop", error=str(e))
                await asyncio.sleep(5)
        
        if self.websocket:
            await self.websocket.close()
        
        logger.info("Onchain worker stopped")

async def main():
    worker = OnchainWorker()
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())