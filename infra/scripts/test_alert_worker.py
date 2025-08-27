# infra/scripts/test_alert_worker.py
import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv
load_dotenv()

from apps.workers.alert_worker import AlertWorker

async def test_alert_worker():
    try:
        worker = AlertWorker()
        
        print(f"Telegram enabled: {worker.telegram_enabled}")
        print("Testing alert monitoring...")
        
        # Run one cycle of monitoring and processing
        await worker.monitor_whale_transactions()
        await worker.process_pending_alerts()
        
        print("Alert worker test completed")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_alert_worker())