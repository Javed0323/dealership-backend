from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Float,
    Text,
    ForeignKey,
)
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime


# ─────────────────────────────────────────────
# CAR  (identity + classification only)
# ─────────────────────────────────────────────
class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    make = Column(String(50), nullable=False, index=True)  # Toyota, BMW
    model = Column(String(50), nullable=False, index=True)  # Camry, X5
    year = Column(Integer, nullable=False, index=True)
    category = Column(String(30), nullable=True)  # Sedan, SUV, Truck
    segment = Column(String(30), nullable=True)  # Compact, Midsize, Fullsize
    description = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    # Relationships
    units = relationship("Inventory", back_populates="car")
    engine = relationship(
        "CarEngine", back_populates="car", uselist=False, cascade="all, delete-orphan"
    )
    dimensions = relationship(
        "CarDimensions",
        back_populates="car",
        uselist=False,
        cascade="all, delete-orphan",
    )
    safety = relationship(
        "CarSafety", back_populates="car", uselist=False, cascade="all, delete-orphan"
    )
    features = relationship(
        "CarFeatures", back_populates="car", uselist=False, cascade="all, delete-orphan"
    )


# ─────────────────────────────────────────────
# ENGINE & PERFORMANCE
# ─────────────────────────────────────────────
class CarEngine(Base):
    __tablename__ = "car_engine"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False, unique=True)

    fuel_type = Column(String(20), nullable=True)  # Petrol, Diesel, Electric, Hybrid
    displacement_cc = Column(Integer, nullable=True)  # in cc  e.g. 2000
    horsepower = Column(Integer, nullable=True)  # hp
    torque_nm = Column(Integer, nullable=True)  # Nm
    transmission = Column(String(20), nullable=True)  # Manual, Automatic, CVT
    transmission_gears = Column(Integer, nullable=True)
    drivetrain = Column(String(10), nullable=True)  # FWD, RWD, AWD, 4WD
    fuel_economy_l100 = Column(Float, nullable=True)  # L/100km
    top_speed_kmh = Column(Integer, nullable=True)  # km/h
    acceleration_sec = Column(Float, nullable=True)  # 0–100 km/h in seconds

    car = relationship("Car", back_populates="engine")


# ─────────────────────────────────────────────
# DIMENSIONS
# ─────────────────────────────────────────────
class CarDimensions(Base):
    __tablename__ = "car_dimensions"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False, unique=True)

    length_mm = Column(Integer, nullable=True)
    width_mm = Column(Integer, nullable=True)
    height_mm = Column(Integer, nullable=True)
    wheelbase_mm = Column(Integer, nullable=True)
    ground_clearance_mm = Column(Integer, nullable=True)
    curb_weight_kg = Column(Integer, nullable=True)
    fuel_tank_l = Column(Integer, nullable=True)
    boot_space_l = Column(Integer, nullable=True)
    doors = Column(Integer, nullable=True)
    seats = Column(Integer, nullable=True)
    tyre_size = Column(String(20), nullable=True)  # 205/55R16

    car = relationship("Car", back_populates="dimensions")


# ─────────────────────────────────────────────
# SAFETY
# ─────────────────────────────────────────────
class CarSafety(Base):
    __tablename__ = "car_safety"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False, unique=True)

    ncap_rating = Column(Integer, nullable=True)  # 0–5 stars
    airbag_count = Column(Integer, nullable=True)

    # Active Safety
    abs = Column(Boolean, default=False)
    esp = Column(Boolean, default=False)
    traction_control = Column(Boolean, default=False)
    hill_start_assist = Column(Boolean, default=False)
    hill_descent_control = Column(Boolean, default=False)

    # ADAS
    lane_keep_assist = Column(Boolean, default=False)
    lane_departure_warning = Column(Boolean, default=False)
    blind_spot_monitor = Column(Boolean, default=False)
    rear_cross_traffic_alert = Column(Boolean, default=False)
    forward_collision_warning = Column(Boolean, default=False)
    auto_emergency_braking = Column(Boolean, default=False)
    traffic_sign_recognition = Column(Boolean, default=False)

    # Parking
    rear_camera = Column(Boolean, default=False)
    surround_view_camera = Column(Boolean, default=False)
    parking_sensors_front = Column(Boolean, default=False)
    parking_sensors_rear = Column(Boolean, default=False)
    self_parking = Column(Boolean, default=False)

    car = relationship("Car", back_populates="safety")


# ─────────────────────────────────────────────
# FEATURES & COMFORT
# ─────────────────────────────────────────────
class CarFeatures(Base):
    __tablename__ = "car_features"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False, unique=True)

    # Comfort
    sunroof = Column(Boolean, default=False)
    panoramic_roof = Column(Boolean, default=False)
    heated_seats = Column(Boolean, default=False)
    ventilated_seats = Column(Boolean, default=False)
    leather_seats = Column(Boolean, default=False)
    memory_seats = Column(Boolean, default=False)
    heated_steering_wheel = Column(Boolean, default=False)

    # Tech & Connectivity
    apple_carplay = Column(Boolean, default=False)
    android_auto = Column(Boolean, default=False)
    wireless_charging = Column(Boolean, default=False)
    keyless_entry = Column(Boolean, default=False)
    push_start = Column(Boolean, default=False)
    remote_start = Column(Boolean, default=False)
    heads_up_display = Column(Boolean, default=False)

    # Infotainment
    infotainment_screen_inch = Column(Float, nullable=True)
    speaker_count = Column(Integer, nullable=True)
    premium_audio = Column(Boolean, default=False)

    # Lighting
    led_headlights = Column(Boolean, default=False)
    adaptive_headlights = Column(Boolean, default=False)
    ambient_lighting = Column(Boolean, default=False)

    # Convenience
    power_tailgate = Column(Boolean, default=False)
    power_mirrors = Column(Boolean, default=False)
    auto_dimming_mirror = Column(Boolean, default=False)
    cruise_control = Column(Boolean, default=False)
    adaptive_cruise_control = Column(Boolean, default=False)

    car = relationship("Car", back_populates="features")


# ─────────────────────────────────────────────
# MEDIA (unchanged)
# ─────────────────────────────────────────────
class CarMedia(Base):
    __tablename__ = "car_media"

    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=False)
    media_type = Column(String(20), nullable=False)  # image, video
    url = Column(String(255), nullable=False)
    alt_text = Column(String(255), nullable=True)
    is_primary = Column(Boolean, default=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    inventory = relationship("Inventory", back_populates="media")
