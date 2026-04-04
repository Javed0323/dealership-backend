# schemas/site_settings.py

from pydantic import BaseModel, EmailStr
from typing import Optional


class SiteSettingsResponse(BaseModel):
    site_name: str
    logo_url: Optional[str]
    theme_color: str | None = None
    timezone: str | None = None
    is_active: bool
    contact_email: str | None = None
    contact_phone: str | None = None
    address: str | None = None
    currency: str | None = None

    class Config:
        from_attributes = True


class SiteSettingsUpdate(BaseModel):
    site_name: Optional[str]
    logo_url: Optional[str]
    theme_color: Optional[str]
    timezone: Optional[str]
    is_active: Optional[bool]
    contact_email: Optional[EmailStr]
    contact_phone: Optional[str]
    address: Optional[str]
    currency: Optional[str]
