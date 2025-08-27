# infra/scripts/test_insert.py
import asyncio
import sys
import os
from datetime import datetime
from decimal import Decimal
import uuid

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv
load_dotenv()

from packages.database.engine import AsyncSessionLocal
from packages.database.models.whale_transaction import WhaleTransaction

async def test_insert():
    try:
        async with AsyncSessionLocal() as session:
            # Create a test whale transaction
            whale_tx = WhaleTransaction(
                tx_hash="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                block_number=18500000,
                timestamp=datetime.utcnow(),
                from_address="0x742d35Cc6634C0532925a3b8D221C5a5c3E9b5e5",
                to_address="0x28C6c06298d514Db089934071355E5743bf21d60",
                value_eth=Decimal("1000.50000000"),
                value_usd=Decimal("1800900.00"),
                gas_used=21000,
                gas_price=20000000000,
                priority_level="high",
                exchange_involved=True,
                ingest_id=str(uuid.uuid4()),
                source="test"
            )
            
            session.add(whale_tx)
            await session.commit()
            
            print(f"Test whale transaction inserted with ID: {whale_tx.id}")
            
            # Query it back to verify
            result = await session.get(WhaleTransaction, whale_tx.id)
            print(f"Retrieved transaction: {result.tx_hash}, Value: {result.value_eth} ETH")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_insert())