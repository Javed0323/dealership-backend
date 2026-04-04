from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
)
from database import Base
from datetime import datetime


class SiteSetting(Base):
    __tablename__ = "site_settings"

    id = Column(Integer, primary_key=True)
    site_name = Column(String(200), nullable=False)
    logo_url = Column(String(500))
    theme_color = Column(String(20), default="#000000")
    currency = Column(String(10), default="PKR")
    timezone = Column(String(50), default="UTC")
    contact_email = Column(String(100))
    contact_phone = Column(String(20))
    address = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
