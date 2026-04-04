from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


# -----------------------------
# Enum (Strongly Recommended)
# -----------------------------


# // Updated schema that doesn't require authentication
class TestDriveStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"  # Added for email/SMS confirmation
    completed = "completed"
    canceled = "canceled"


# -----------------------------
# Booking Schema (No Auth Required)
# -----------------------------
class TestDriveBase(BaseModel):
    # Customer info (collected in form)
    full_name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    phone: str = Field(..., min_length=10, max_length=15)

    # Booking details
    inventory_id: int
    scheduled_at: datetime
    status: TestDriveStatus = TestDriveStatus.pending
    notes: Optional[str] = Field(None, max_length=255)


# For confirmation (optional but recommended)
class TestDriveConfirmation(BaseModel):
    booking_id: int
    confirmation_token: str  # Sent via email/SMS
    confirmed_at: Optional[datetime]


# -----------------------------
# Create Schema (POST)
# -----------------------------
class TestDriveCreate(TestDriveBase):
    pass


# -----------------------------
# Update Schema (PUT / PATCH)
# -----------------------------
class TestDriveUpdate(BaseModel):
    inventory_id: Optional[int] = None
    customer_id: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[TestDriveStatus] = None
    notes: Optional[str] = Field(None, max_length=255)


# -----------------------------
# Response Schema (GET)
# -----------------------------
class TestDriveResponse(TestDriveBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
