from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# -----------------------------
# Base Schema (Shared Fields)
# -----------------------------
class SaleBase(BaseModel):
    customer_id: int | None = None
    customer_name: str | None = None
    inventory_id: int
    sale_price: float
    sale_status: str | None = None
    sale_date: datetime | None = None
    payment_status: str | None = "pending"
    invoice_number: str | None = None


# -----------------------------
# Create Schema (POST)
# -----------------------------
class SaleCreate(SaleBase):
    pass


# -----------------------------
# Update Schema (PUT / PATCH)
# -----------------------------
class SaleUpdate(BaseModel):
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    inventory_id: Optional[int] = None
    sale_price: Optional[float] = None
    sale_status: str | None = None
    sale_date: datetime | None = None
    payment_status: Optional[str] = None
    invoice_number: Optional[str] = None


# -----------------------------
# Response Schema (GET)
# -----------------------------
class SaleResponse(SaleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy compatibility (Pydantic v2)
