# packages/database/models/base.py
from sqlalchemy import Column, DateTime, func
from packages.database.engine import Base

class BaseModel(Base):
    """Base model that all tables will inherit"""
    __abstract__ = True  # This line makes sure that no table is created for this model
    
    # All tables will have created_at
    created_at = Column(DateTime(timezone=True), server_default=func.now())