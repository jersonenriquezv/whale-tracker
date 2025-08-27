# packages/database/models/whale_transaction.py
from sqlalchemy import Column, String, BigInteger, DECIMAL, Boolean, DateTime, Index
from sqlalchemy.sql import func
from packages.database.models.base import BaseModel

class WhaleTransaction(BaseModel):
    __tablename__ = "whale_transactions"
    
    # Main fields
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tx_hash = Column(String(66), unique=True, nullable=False, index=True)
    block_number = Column(BigInteger, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    from_address = Column(String(42), nullable=False)
    to_address = Column(String(42), nullable=False)
    value_eth = Column(DECIMAL(20, 8), nullable=False)
    value_usd = Column(DECIMAL(15, 2))
    gas_used = Column(BigInteger)
    gas_price = Column(BigInteger)
    priority_level = Column(String(10), nullable=False)  # 'high', 'normal'
    exchange_involved = Column(Boolean, default=False)
    
    # Audit fields
    ingest_id = Column(String(36))  # To avoid duplicates    
    source = Column(String(20), default='alchemy')
    
    # Indexes to improve performance
    __table_args__ = (
        Index('idx_whale_tx_timestamp', 'timestamp'),
        Index('idx_whale_tx_value', 'value_eth'),
        Index('idx_whale_tx_priority', 'priority_level', 'timestamp'),
        Index('idx_whale_tx_block', 'block_number'),
    )