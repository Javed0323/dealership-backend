from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


# ─────────────────────────────────────────────
# CAR ENGINE
# ─────────────────────────────────────────────
class CarEngineBase(BaseModel):
    fuel_type: Optional[str] = None  # Petrol, Diesel, Electric, Hybrid
    displacement_cc: Optional[int] = None
    horsepower: Optional[int] = None
    torque_nm: Optional[int] = None
    transmission: Optional[str] = None  # Manual, Automatic, CVT
    transmission_gears: Optional[int] = None
    drivetrain: Optional[str] = None  # FWD, RWD, AWD, 4WD
    fuel_economy_l100: Optional[float] = None
    top_speed_kmh: Optional[int] = None
    acceleration_sec: Optional[float] = None


class CarEngineCreate(CarEngineBase):
    pass


class CarEngineRead(CarEngineBase):
    id: int
    car_id: int
    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────────────────────
# CAR DIMENSIONS
# ─────────────────────────────────────────────
class CarDimensionsBase(BaseModel):
    length_mm: Optional[int] = None
    width_mm: Optional[int] = None
    height_mm: Optional[int] = None
    wheelbase_mm: Optional[int] = None
    ground_clearance_mm: Optional[int] = None
    curb_weight_kg: Optional[int] = None
    fuel_tank_l: Optional[int] = None
    boot_space_l: Optional[int] = None
    doors: Optional[int] = None
    seats: Optional[int] = None
    tyre_size: Optional[str] = None


class CarDimensionsCreate(CarDimensionsBase):
    pass


class CarDimensionsRead(CarDimensionsBase):
    id: int
    car_id: int
    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────────────────────
# CAR SAFETY
# ─────────────────────────────────────────────
class CarSafetyBase(BaseModel):
    ncap_rating: Optional[int] = None
    airbag_count: Optional[int] = None
    abs: bool = False
    esp: bool = False
    traction_control: bool = False
    hill_start_assist: bool = False
    hill_descent_control: bool = False
    lane_keep_assist: bool = False
    lane_departure_warning: bool = False
    blind_spot_monitor: bool = False
    rear_cross_traffic_alert: bool = False
    forward_collision_warning: bool = False
    auto_emergency_braking: bool = False
    traffic_sign_recognition: bool = False
    rear_camera: bool = False
    surround_view_camera: bool = False
    parking_sensors_front: bool = False
    parking_sensors_rear: bool = False
    self_parking: bool = False


class CarSafetyCreate(CarSafetyBase):
    pass


class CarSafetyRead(CarSafetyBase):
    id: int
    car_id: int
    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────────────────────
# CAR FEATURES
# ─────────────────────────────────────────────
class CarFeaturesBase(BaseModel):
    # Comfort
    sunroof: bool = False
    panoramic_roof: bool = False
    heated_seats: bool = False
    ventilated_seats: bool = False
    leather_seats: bool = False
    memory_seats: bool = False
    heated_steering_wheel: bool = False
    # Tech
    apple_carplay: bool = False
    android_auto: bool = False
    wireless_charging: bool = False
    keyless_entry: bool = False
    push_start: bool = False
    remote_start: bool = False
    heads_up_display: bool = False
    # Infotainment
    infotainment_screen_inch: Optional[float] = None
    speaker_count: Optional[int] = None
    premium_audio: bool = False
    # Lighting
    led_headlights: bool = False
    adaptive_headlights: bool = False
    ambient_lighting: bool = False
    # Convenience
    power_tailgate: bool = False
    power_mirrors: bool = False
    auto_dimming_mirror: bool = False
    cruise_control: bool = False
    adaptive_cruise_control: bool = False


class CarFeaturesCreate(CarFeaturesBase):
    pass


class CarFeaturesRead(CarFeaturesBase):
    id: int
    car_id: int
    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────────────────────
# CAR MEDIA
# ─────────────────────────────────────────────


# ─────────────────────────────────────────────
# CAR  (core)
# ─────────────────────────────────────────────
class CarBase(BaseModel):
    make: str
    model: str
    year: int
    category: Optional[str] = None  # Sedan, SUV, Truck
    segment: Optional[str] = None  # Compact, Midsize, Fullsize
    description: Optional[str] = None


class CarCreate(CarBase):
    engine: Optional[CarEngineCreate] = None
    dimensions: Optional[CarDimensionsCreate] = None
    safety: Optional[CarSafetyCreate] = None
    features: Optional[CarFeaturesCreate] = None


class CarUpdate(BaseModel):
    # All optional — partial updates
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    category: Optional[str] = None
    segment: Optional[str] = None
    description: Optional[str] = None
    engine: Optional[CarEngineCreate] = None
    dimensions: Optional[CarDimensionsCreate] = None
    safety: Optional[CarSafetyCreate] = None
    features: Optional[CarFeaturesCreate] = None


class CarRead(CarBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    engine: Optional[CarEngineRead] = None
    dimensions: Optional[CarDimensionsRead] = None
    safety: Optional[CarSafetyRead] = None
    features: Optional[CarFeaturesRead] = None

    model_config = ConfigDict(from_attributes=True)
