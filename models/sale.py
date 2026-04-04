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


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(
        Integer, ForeignKey("customers.id"), nullable=True
    )  # optional if we want to allow walk-ins
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=False)
    customer_name = Column(
        String(100), nullable=True
    )  # capture at sale time for walk-ins

    sale_price = Column(Float, nullable=False)
    payment_status = Column(String(50), default="pending")  # pending, paid, overdue
    invoice_number = Column(String(100), unique=True, nullable=True)
    sale_date = Column(DateTime, default=datetime.utcnow)
    sale_status = Column(String(50), default="draft")  # draft, completed, canceled

    # Relationships
    customer = relationship("Customer", back_populates="sales")
    inventory = relationship("Inventory", back_populates="sales")
    payments = relationship(
        "Payment", back_populates="sale", cascade="all, delete-orphan"
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
