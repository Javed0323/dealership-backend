from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
)
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String, unique=True)
    password = Column(String(255))
    role = Column(String, default="user")
    is_verified = Column(Boolean, default=False)
    last_verification_sent = Column(DateTime, nullable=True)
    # relationships
    customer = relationship(
        "Customer", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
