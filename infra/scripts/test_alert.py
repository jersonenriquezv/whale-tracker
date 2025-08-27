# infra/scripts/test_alert.py
import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv
load_dotenv()

from packages.database.engine import AsyncSessionLocal
from packages.database.models.alert import Alert

async def test_alert():
    try:
        async with AsyncSessionLocal() as session:
            # Create a test alert
            test_alert = Alert(
                alert_type="whale_transfer",
                priority="high",
                title="Test Whale Alert",
                message="This is a test alert for a whale transaction",
                related_tx_hash="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                status="pending"
            )
            
            session.add(test_alert)
            await session.commit()
            
            print(f"Test alert inserted with ID: {test_alert.id}")
            
            # Query it back
            result = await session.get(Alert, test_alert.id)
            print(f"Retrieved alert: {result.title}, Status: {result.status}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_alert())