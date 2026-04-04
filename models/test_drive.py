from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum


class TestDriveStatus(str, PyEnum):
    pending = "pending"
    completed = "completed"
    canceled = "canceled"


class TestDrive(Base):
    __tablename__ = "test_drives"

    id = Column(Integer, primary_key=True, index=True)

    # Customer info (captured directly, no auth needed)
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)

    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=False)

    scheduled_at = Column(DateTime, nullable=False)
    status = Column(String(30), default=TestDriveStatus.pending.value)
    notes = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    # Relationships
    inventory = relationship("Inventory", back_populates="test_drives")
