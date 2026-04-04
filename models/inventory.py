from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum, Text
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False, index=True)

    # ── Identification ─────────────────────────────────────
    vin = Column(String(50), unique=True, nullable=True)
    registration_number = Column(String(50), unique=True, nullable=True)
    stock_number = Column(String(30), unique=True, nullable=True)  # internal ref

    # ── Physical (per-unit) ────────────────────────────────
    exterior_color = Column(String(30), nullable=True)
    interior_color = Column(String(30), nullable=True)
    mileage_km = Column(Integer, nullable=True)  # integer is fine for mileage

    # ── Condition & Status ─────────────────────────────────
    condition = Column(
        Enum("new", "used", "refurbished", name="unit_condition"), nullable=False
    )
    status = Column(
        Enum("available", "reserved", "sold", "maintenance", name="inventory_status"),
        nullable=False,
        default="available",
        index=True,
    )

    # ── Pricing ────────────────────────────────────────────
    purchase_price = Column(Float, nullable=True)  # what dealer paid
    selling_price = Column(Float, nullable=False)  # listed price
    discounted_price = Column(Float, nullable=True)  # optional promo price

    # ── Purchase Info ──────────────────────────────────────
    purchased_at = Column(DateTime, nullable=True)  # no default — enter explicitly
    location = Column(String(100), nullable=False, default="Main Showroom")

    # ── Internal ───────────────────────────────────────────
    notes = Column(Text, nullable=True)  # admin-only notes on this unit

    # ── Timestamps ─────────────────────────────────────────
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    # ── Relationships ──────────────────────────────────────
    media = relationship(
        "CarMedia", back_populates="inventory", cascade="all, delete-orphan"
    )
    car = relationship("Car", back_populates="units")
    sales = relationship("Sale", back_populates="inventory")
    offers = relationship(
        "Offer", back_populates="inventory", cascade="all, delete-orphan"
    )
    test_drives = relationship(
        "TestDrive", back_populates="inventory", cascade="all, delete-orphan"
    )
