# infra/scripts/create_tables.py
import asyncio
import sys
import os
from dotenv import load_dotenv
from sqlalchemy import text

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Load environment variables
load_dotenv()

# Import engine and models
from packages.database.engine import engine, Base
from packages.database.models.whale_transaction import WhaleTransaction
from packages.database.models.alert import Alert  # Add this import

async def create_tables():
    try:
        print("Creating tables in database...")
        
        # Create all tables defined in Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("Tables created successfully!")
        
        # Verify tables exist
        async with engine.begin() as conn:
            result = await conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            )
            tables = result.fetchall()
            print(f"Tables in database: {[table[0] for table in tables]}")
        
        await engine.dispose()
        
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    asyncio.run(create_tables())