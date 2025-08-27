"""
Debug script to check transactions in database
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv()

from packages.database.engine import AsyncSessionLocal
from packages.database.models.whale_transaction import WhaleTransaction
from packages.database.models.alert import Alert
from sqlalchemy import select, and_

async def debug_transactions():
    """Debug what transactions are in the database"""
    
    try:
        async with AsyncSessionLocal() as session:
            # First, let's see ALL transactions
            print("🔍 CHECKING ALL TRANSACTIONS IN DATABASE")
            print("="*80)
            
            all_query = select(WhaleTransaction).order_by(WhaleTransaction.created_at.desc()).limit(20)
            all_result = await session.execute(all_query)
            all_transactions = all_result.scalars().all()
            
            print(f"📊 Total transactions found: {len(all_transactions)}")
            
            if all_transactions:
                print("\n📋 RECENT TRANSACTIONS:")
                for tx in all_transactions:
                    print(f"   🔍 {tx.tx_hash[:10]}... - {tx.value_eth} ETH ({tx.priority_level}) - {tx.created_at}")
            else:
                print("❌ No transactions found in database!")
                return
            
            # Check for existing alerts
            print("\n" + "="*80)
            print("🔔 CHECKING EXISTING ALERTS")
            print("="*80)
            
            alerts_query = select(Alert).order_by(Alert.created_at.desc()).limit(10)
            alerts_result = await session.execute(alerts_query)
            alerts = alerts_result.scalars().all()
            
            print(f"📊 Total alerts found: {len(alerts)}")
            
            for alert in alerts:
                print(f"   🔔 Alert {alert.id}: {alert.alert_type} - {alert.status} - {alert.created_at}")
                if alert.related_tx_hash:
                    print(f"      TX: {alert.related_tx_hash[:10]}...")
            
            # Now check recent transactions (last 10 minutes)
            cutoff_time = datetime.utcnow().replace(tzinfo=None) - timedelta(minutes=10)
            
            recent_query = select(WhaleTransaction).where(
                WhaleTransaction.created_at >= cutoff_time
            ).order_by(WhaleTransaction.created_at.desc())
            
            recent_result = await session.execute(recent_query)
            recent_transactions = recent_result.scalars().all()
            
            print(f"\n📊 Found {len(recent_transactions)} transactions in last 10 minutes")
            
            # Now check what the alert worker would find
            print("\n" + "="*80)
            print("🔍 ALERT WORKER QUERY SIMULATION")
            print("="*80)
            
            # Simulate alert worker query (last 5 minutes)
            five_min_ago = datetime.utcnow().replace(tzinfo=None) - timedelta(minutes=5)
            
            print(f"🔍 Querying for transactions >= {five_min_ago}")
            print(f"🔍 Priority levels: ['high', 'normal']")
            
            # Test the query step by step
            print("\n📊 STEP 1: All transactions in last 5 minutes:")
            step1_query = select(WhaleTransaction).where(
                WhaleTransaction.created_at >= five_min_ago
            )
            step1_result = await session.execute(step1_query)
            step1_transactions = step1_result.scalars().all()
            print(f"   Found: {len(step1_transactions)} transactions")
            
            print("\n📊 STEP 2: High priority transactions in last 5 minutes:")
            step2_query = select(WhaleTransaction).where(
                and_(
                    WhaleTransaction.priority_level == "high",
                    WhaleTransaction.created_at >= five_min_ago
                )
            )
            step2_result = await session.execute(step2_query)
            step2_transactions = step2_result.scalars().all()
            print(f"   Found: {len(step2_transactions)} high priority transactions")
            
            print("\n📊 STEP 3: Normal priority transactions in last 5 minutes:")
            step3_query = select(WhaleTransaction).where(
                and_(
                    WhaleTransaction.priority_level == "normal",
                    WhaleTransaction.created_at >= five_min_ago
                )
            )
            step3_result = await session.execute(step3_query)
            step3_transactions = step3_result.scalars().all()
            print(f"   Found: {len(step3_transactions)} normal priority transactions")
            
            # Final alert worker query
            alert_query = select(WhaleTransaction).where(
                and_(
                    WhaleTransaction.priority_level.in_(["high", "normal"]),
                    WhaleTransaction.created_at >= five_min_ago
                )
            )
            
            alert_result = await session.execute(alert_query)
            alert_transactions = alert_result.scalars().all()
            
            print(f"\n🎯 FINAL: Alert worker would find: {len(alert_transactions)} transactions")
            
            for tx in alert_transactions:
                # Check if alert already exists for this transaction
                existing_alert_query = select(Alert).where(Alert.related_tx_hash == tx.tx_hash)
                existing_alert_result = await session.execute(existing_alert_query)
                existing_alert = existing_alert_result.scalar_one_or_none()
                
                if existing_alert:
                    print(f"   ⚠️  {tx.tx_hash[:10]}... - {tx.value_eth} ETH ({tx.priority_level}) - ALERT EXISTS")
                else:
                    print(f"   ✅ {tx.tx_hash[:10]}... - {tx.value_eth} ETH ({tx.priority_level}) - NO ALERT")
            
            # Check time ranges
            print("\n" + "="*80)
            print("⏰ TIME ANALYSIS")
            print("="*80)
            
            now = datetime.utcnow().replace(tzinfo=None)
            print(f"Current time (UTC): {now}")
            print(f"Cutoff time (5 min ago): {five_min_ago}")
            print(f"Cutoff time (10 min ago): {cutoff_time}")
            
            if all_transactions:
                oldest = min(tx.created_at.replace(tzinfo=None) for tx in all_transactions)
                newest = max(tx.created_at.replace(tzinfo=None) for tx in all_transactions)
                print(f"Oldest transaction: {oldest}")
                print(f"Newest transaction: {newest}")
                
                # Check if transactions are within 5 minutes
                recent_count = sum(1 for tx in all_transactions if tx.created_at.replace(tzinfo=None) >= five_min_ago)
                print(f"Transactions in last 5 minutes: {recent_count}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_transactions())
