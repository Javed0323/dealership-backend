from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


# -----------------------------
# Enums (Strongly Recommended)
# -----------------------------
class PaymentMethod(str, Enum):
    cash = "cash"
    card = "card"
    bank_transfer = "bank_transfer"


class PaymentStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


# -----------------------------
# Base Schema (Shared Fields)
# -----------------------------
class PaymentBase(BaseModel):
    sale_id: int
    amount: float = Field(..., gt=0)
    payment_method: PaymentMethod
    status: Optional[PaymentStatus] = PaymentStatus.pending
    paid_at: Optional[datetime] = None


# -----------------------------
# Create Schema (POST)
# -----------------------------
class PaymentCreate(PaymentBase):
    pass


# -----------------------------
# Update Schema (PUT / PATCH)
# -----------------------------
class PaymentUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)  # Example: Minimum payment amount
    payment_method: Optional[PaymentMethod] = None
    status: Optional[PaymentStatus] = None
    paid_at: Optional[datetime] = None


# -----------------------------
# Response Schema (GET)
# -----------------------------
class PaymentResponse(PaymentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
