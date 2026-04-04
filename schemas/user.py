from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import date, datetime


class UserBase(BaseModel):
    email: EmailStr
    password: str
    role: Optional[str] = Field(default="customer", description="Role of the user")
    username: Optional[str] = Field(default=None, description="Username of the user")


class UserCreate(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    username: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # this tells pydantic to work with SQLAlchemy models
