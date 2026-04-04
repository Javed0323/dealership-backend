from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


# -----------------------------
# Base Schema (Shared Fields)
# -----------------------------
class OfferBase(BaseModel):
    inventory_id: int
    title: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    discount_percentage: float = Field(..., gt=0, le=100)
    start_date: datetime
    end_date: datetime
    is_active: Optional[bool] = True

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, value, info):
        start_date = info.data.get("start_date")
        if start_date and value <= start_date:
            raise ValueError("end_date must be after start_date")
        return value


# -----------------------------
# Create Schema (POST)
# -----------------------------
class OfferCreate(OfferBase):
    pass


# -----------------------------
# Update Schema (PUT / PATCH)
# -----------------------------
class OfferUpdate(BaseModel):
    inventory_id: Optional[int] = None
    title: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    discount_percentage: Optional[float] = Field(None, gt=0, le=100)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, value, info):
        start_date = info.data.get("start_date")
        if start_date and value and value <= start_date:
            raise ValueError("end_date must be after start_date")
        return value


# -----------------------------
# Response Schema (GET)
# -----------------------------
class OfferResponse(OfferBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
