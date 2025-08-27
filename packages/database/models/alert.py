# packages/database/models/alert.py
from sqlalchemy import Column, String, BigInteger, Boolean, DateTime, Text, Index
from sqlalchemy.sql import func
from packages.database.models.base import BaseModel

class Alert(BaseModel):
    __tablename__ = "alerts"
    
    # Main fields
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    alert_type = Column(String(30), nullable=False)  # 'whale_transfer', 'liquidation_sweep', 'smc_pattern'
    priority = Column(String(10), nullable=False)    # 'high', 'medium', 'low'
    title = Column(String(200), nullable=False)      # Alert title
    message = Column(Text, nullable=False)           # Alert message content
    
    # Related data
    related_tx_hash = Column(String(66))             # Related whale transaction hash
    related_data = Column(Text)                      # JSON data for additional context
    
    # Alert status
    status = Column(String(20), default='pending')   # 'pending', 'sent', 'failed'
    sent_to_telegram = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True))
    error_message = Column(Text)                     # Error details if sending failed
    
    # Processing info
    processed_by = Column(String(50))                # Worker that processed this alert
    retry_count = Column(BigInteger, default=0)      # Number of retry attempts
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_alerts_status', 'status', 'created_at'),
        Index('idx_alerts_priority', 'priority', 'created_at'),
        Index('idx_alerts_type', 'alert_type', 'created_at'),
        Index('idx_alerts_pending', 'status', 'priority'),  # For alert worker queries
    )