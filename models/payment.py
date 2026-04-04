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


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)

    amount = Column(Float, nullable=False)  # Payment amount
    payment_method = Column(
        String(50), nullable=False
    )  # Cash, Card, Bank Transfer, etc.
    status = Column(String(30), default="pending")  # pending, completed, failed
    paid_at = Column(DateTime, default=datetime.utcnow)  # Timestamp of payment
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    # Relationship
    sale = relationship("Sale", back_populates="payments")
