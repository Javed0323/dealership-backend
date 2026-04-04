from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Float,
    Text,
    Date,
    JSON,
    ForeignKey,
)
from sqlalchemy.sql import func
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=False)

    title = Column(String(100), nullable=False)  # Offer name or title
    description = Column(String(255), nullable=True)  # Short description
    discount_percentage = Column(Float, nullable=False)  # 10.0 = 10%
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)  # Can manually deactivate offer
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    # Relationship
    inventory = relationship("Inventory", back_populates="offers")
