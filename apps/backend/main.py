"""
Whale Tracker v0 - Backend API
FastAPI application for whale transaction tracking and analysis
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from packages.database.engine import AsyncSessionLocal
from packages.database.models.whale_transaction import WhaleTransaction

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title="Whale Tracker v0 API",
    description="API for tracking whale transactions and market analysis",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting Whale Tracker v0 Backend API")
         
    # Log environment information
    logger.info("Environment",
                 environment=os.getenv("ENVIRONMENT", "development"),
                debug=os.getenv("DEBUG", "false"))

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down Whale Tracker v0 Backend API")

@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint"""
    return {
        "message": "Whale Tracker v0 API",
        "version": "0.1.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    try:
        # Test database connection
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(1))
            db_status = "healthy"
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        db_status = "unhealthy"
             
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
        "services": {
            "api": "healthy",
            "database": db_status,
            "redis": "not_implemented"
        }
    }

@app.get("/status")
async def status() -> Dict[str, Any]:
    """System status endpoint"""
    return {
        "status": "operational",
        "uptime": "not_implemented",
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/whales/recent")
async def get_recent_whales(
    limit: int = Query(default=10, le=100, ge=1),
    hours_back: int = Query(default=24, le=168, ge=1),
    priority_level: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db)
):
    """Get recent whale transactions"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        query = select(WhaleTransaction).where(
            WhaleTransaction.timestamp >= cutoff_time
        )
        
        if priority_level:
            query = query.where(WhaleTransaction.priority_level == priority_level)
        
        query = query.order_by(desc(WhaleTransaction.timestamp)).limit(limit)
        result = await db.execute(query)
        whales = result.scalars().all()
        
        whale_list = []
        for whale in whales:
            whale_dict = {
                "id": whale.id,
                "tx_hash": whale.tx_hash,
                "block_number": whale.block_number,
                "timestamp": whale.timestamp.isoformat(),
                "from_address": whale.from_address,
                "to_address": whale.to_address,
                "value_eth": float(whale.value_eth),
                "value_usd": float(whale.value_usd) if whale.value_usd else None,
                "priority_level": whale.priority_level,
                "exchange_involved": whale.exchange_involved,
                "source": whale.source
            }
            whale_list.append(whale_dict)
        
        return {
            "whales": whale_list,
            "count": len(whale_list),
            "limit": limit,
            "hours_back": hours_back
        }
        
    except Exception as e:
        logger.error("Error fetching recent whales", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/whales/stats")
async def get_whale_stats(
    hours_back: int = Query(default=24, le=168, ge=1),
    db: AsyncSession = Depends(get_db)
):
    """Get whale transaction statistics"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        query = select(WhaleTransaction).where(
            WhaleTransaction.timestamp >= cutoff_time
        )
        result = await db.execute(query)
        whales = result.scalars().all()
        
        if not whales:
            return {
                "total_transactions": 0,
                "total_volume_eth": 0,
                "high_priority_count": 0,
                "normal_priority_count": 0,
                "exchange_transactions": 0,
                "hours_back": hours_back
            }
        
        total_volume = sum(whale.value_eth for whale in whales)
        high_priority = len([w for w in whales if w.priority_level == "high"])
        normal_priority = len([w for w in whales if w.priority_level == "normal"])
        exchange_involved = len([w for w in whales if w.exchange_involved])
        
        return {
            "total_transactions": len(whales),
            "total_volume_eth": float(total_volume),
            "high_priority_count": high_priority,
            "normal_priority_count": normal_priority,
            "exchange_transactions": exchange_involved,
            "largest_transaction_eth": float(max(whale.value_eth for whale in whales)),
            "hours_back": hours_back
        }
        
    except Exception as e:
        logger.error("Error fetching whale stats", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/whales/{tx_hash}")
async def get_whale_by_hash(
    tx_hash: str,
    db: AsyncSession = Depends(get_db)
):
    """Get specific whale transaction by hash"""
    try:
        query = select(WhaleTransaction).where(WhaleTransaction.tx_hash == tx_hash)
        result = await db.execute(query)
        whale = result.scalar_one_or_none()
        
        if not whale:
            raise HTTPException(status_code=404, detail="Whale transaction not found")
        
        return {
            "id": whale.id,
            "tx_hash": whale.tx_hash,
            "block_number": whale.block_number,
            "timestamp": whale.timestamp.isoformat(),
            "from_address": whale.from_address,
            "to_address": whale.to_address,
            "value_eth": float(whale.value_eth),
            "value_usd": float(whale.value_usd) if whale.value_usd else None,
            "priority_level": whale.priority_level,
            "exchange_involved": whale.exchange_involved,
            "gas_used": whale.gas_used,
            "gas_price": whale.gas_price,
            "source": whale.source,
            "created_at": whale.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching whale by hash", tx_hash=tx_hash, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )