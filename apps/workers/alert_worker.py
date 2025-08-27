# apps/workers/alert_worker.py
import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv
import structlog
import aiohttp

load_dotenv()

from packages.database.engine import AsyncSessionLocal
from packages.database.models.alert import Alert
from packages.database.models.whale_transaction import WhaleTransaction
from sqlalchemy import select, and_

# Reduce SQLAlchemy logging to reduce noise
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

logger = structlog.get_logger()

class AlertWorker:
    def __init__(self):
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not self.telegram_bot_token or not self.telegram_chat_id:
            logger.warning("Telegram credentials not configured, alerts will be logged only")
            self.telegram_enabled = False
        else:
            self.telegram_enabled = True
            self.telegram_api_url = f"https://api.telegram.org/bot{self.telegram_bot_token}"
        
        # Alert settings
        self.max_alerts_per_minute = int(os.getenv("MAX_ALERTS_PER_MINUTE", "3"))
        self.max_retry_attempts = 3
        self.retry_delay = 60  # seconds
        
        self.running = False
    
    async def monitor_whale_transactions(self):
        """Monitor new whale transactions and create alerts"""
        try:
            async with AsyncSessionLocal() as session:
                # Get recent high priority whales that don't have alerts yet
                cutoff_time = datetime.utcnow().replace(tzinfo=None) - timedelta(minutes=5)  # Last 5 minutes
                
                # Query for high priority whales without existing alerts
                from sqlalchemy import func
                whale_query = select(WhaleTransaction).where(
                    and_(
                        WhaleTransaction.priority_level.in_(["high", "normal"]),  # Include both high and normal
                        func.timezone('UTC', WhaleTransaction.created_at) >= cutoff_time
                    )
                )
                
                result = await session.execute(whale_query)
                whales = result.scalars().all()
                
                logger.info(f"Found {len(whales)} high priority whales in last 5 minutes")
                
                for whale in whales:
                    # Check if alert already exists for this transaction
                    alert_query = select(Alert).where(
                        Alert.related_tx_hash == whale.tx_hash
                    )
                    alert_result = await session.execute(alert_query)
                    existing_alert = alert_result.scalar_one_or_none()
                    
                    if not existing_alert:
                        await self.create_whale_alert(session, whale)
                
                await session.commit()
                
        except Exception as e:
            logger.error("Error monitoring whale transactions", error=str(e))
    
    async def create_whale_alert(self, session, whale: WhaleTransaction):
        """Create an alert for a whale transaction"""
        try:
            # Format alert message
            eth_amount = float(whale.value_eth)
            usd_amount = float(whale.value_usd) if whale.value_usd else 0
            
            title = f"Large Whale Transfer: {eth_amount:.2f} ETH"

            tx_hash = whale.tx_hash if whale.tx_hash.startswith('0x') else f"0x{whale.tx_hash}"
            
            message = f"""
🐋 **WHALE ALERT** 🚨

**Amount:** {eth_amount:.2f} ETH (${usd_amount:,.2f})
**Priority:** {whale.priority_level.upper()}
**Exchange Involved:** {'Yes' if whale.exchange_involved else 'No'}

**From:** `{whale.from_address}`
**To:** `{whale.to_address}`

**Transaction:** `{tx_hash}`
**Block:** {whale.block_number}
**Time:** {whale.timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC

**Etherscan:** https://etherscan.io/block/{whale.block_number}
""".strip()
            
            # Create alert record
            alert = Alert(
                alert_type="whale_transfer",
                priority="high",
                title=title,
                message=message,
                related_tx_hash=whale.tx_hash,
                related_data=json.dumps({
                    "whale_id": whale.id,
                    "value_eth": float(whale.value_eth),
                    "value_usd": float(whale.value_usd) if whale.value_usd else None,
                    "exchange_involved": whale.exchange_involved
                }),
                status="pending"
            )
            
            session.add(alert)
            logger.info(f"Created whale alert for tx: {whale.tx_hash[:10]}...")
            
        except Exception as e:
            logger.error("Error creating whale alert", error=str(e))
    
    async def process_pending_alerts(self):
        """Process pending alerts and send them"""
        try:
            async with AsyncSessionLocal() as session:
                # Get pending alerts ordered by priority and creation time
                query = select(Alert).where(
                    and_(
                        Alert.status == "pending",
                        Alert.retry_count < self.max_retry_attempts
                    )
                ).order_by(
                    Alert.priority.desc(),  # high priority first
                    Alert.created_at.asc()  # oldest first
                ).limit(self.max_alerts_per_minute)
                
                result = await session.execute(query)
                pending_alerts = result.scalars().all()
                
                logger.info(f"Found {len(pending_alerts)} pending alerts to process")
                
                for alert in pending_alerts:
                    success = await self.send_alert(alert)
                    
                    if success:
                        alert.status = "sent"
                        alert.sent_to_telegram = True
                        alert.sent_at = datetime.utcnow().replace(tzinfo=None)
                        logger.info(f"Alert sent successfully: {alert.id}")
                    else:
                        alert.retry_count += 1
                        if alert.retry_count >= self.max_retry_attempts:
                            alert.status = "failed"
                            logger.error(f"Alert failed after {self.max_retry_attempts} retries: {alert.id}")
                
                await session.commit()
                
        except Exception as e:
            logger.error("Error processing pending alerts", error=str(e))
    
    async def send_alert(self, alert: Alert) -> bool:
        """Send alert via Telegram"""
        if not self.telegram_enabled:
            # Just log the alert if Telegram is not configured
            logger.info("Alert (Telegram disabled)", 
                       alert_type=alert.alert_type,
                       priority=alert.priority,
                       title=alert.title)
            return True
        
        try:
            # Send message to Telegram
            url = f"{self.telegram_api_url}/sendMessage"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": alert.message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        return True
                    else:
                        error_text = await response.text()
                        alert.error_message = f"HTTP {response.status}: {error_text}"
                        logger.error("Telegram API error", 
                                   status=response.status, 
                                   error=error_text)
                        return False
                        
        except Exception as e:
            alert.error_message = str(e)
            logger.error("Error sending Telegram alert", error=str(e))
            return False
    
    async def cleanup_old_alerts(self):
        """Clean up old alerts (keep for 7 days)"""
        try:
            async with AsyncSessionLocal() as session:
                cutoff_time = datetime.utcnow().replace(tzinfo=None) - timedelta(days=7)
                
                # Delete old alerts
                from sqlalchemy import delete, func
                stmt = delete(Alert).where(func.timezone('UTC', Alert.created_at) < cutoff_time)
                result = await session.execute(stmt)
                deleted_count = result.rowcount
                
                await session.commit()
                
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} old alerts")
                    
        except Exception as e:
            logger.error("Error cleaning up old alerts", error=str(e))
    
    async def run(self):
        """Main alert worker loop"""
        self.running = True
        logger.info("Starting alert worker")
        
        if not self.telegram_enabled:
            logger.warning("Alert worker started without Telegram configuration")
        
        while self.running:
            try:
                # Monitor for new whale transactions
                await self.monitor_whale_transactions()
                
                # Process pending alerts
                await self.process_pending_alerts()
                
                # Cleanup old alerts (run less frequently)
                if datetime.utcnow().minute % 30 == 0:  # Every 30 minutes
                    await self.cleanup_old_alerts()
                
                # Wait before next cycle
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                logger.info("Shutdown requested")
                self.running = False
            except Exception as e:
                logger.error("Unexpected error in alert worker", error=str(e))
                await asyncio.sleep(60)  # Wait longer on error
        
        logger.info("Alert worker stopped")

async def main():
    worker = AlertWorker()
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())