from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from schemas import CarBase


# --- Base schema with shared fields ---
class InventoryBase(BaseModel):
    car_id: int
    vin: str
    registration_number: str | None = None
    stock_number: str
    exterior_color: str
    interior_color: str
    mileage_km: int
    purchase_price: float
    selling_price: float
    discounted_price: float
    status: str | None = None
    condition: str
    location: str | None = None
    notes: str


# schemas.py


class CarMediaOut(BaseModel):
    id: int
    url: str
    alt_text: str | None = None
    is_primary: bool
    media_type: str

    model_config = ConfigDict(from_attributes=True)


class CarOut(CarBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InventoryOut(InventoryBase):
    id: int
    created_at: datetime
    media: list[CarMediaOut] = []
    car: CarOut  # ← adds the nested Car + media on top of base fields

    model_config = ConfigDict(from_attributes=True)


# --- Schema for creating a new inventory unit ---
class InventoryCreate(InventoryBase):
    pass


# --- Schema for updating an inventory unit ---
class InventoryUpdate(BaseModel):
    car_id: int
    vin: str | None = None
    registration_number: str | None = None
    stock_number: str | None = None
    exterior_color: str | None = None
    interior_color: str | None = None
    mileage_km: int | None = None
    purchase_price: float | None = None
    selling_price: float | None = None
    discounted_price: float | None = None
    status: str | None = None
    condition: str | None = None
    location: str | None = None
    notes: str | None = None


# --- Schema for reading inventory (response) ---
class InventoryResponse(InventoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
