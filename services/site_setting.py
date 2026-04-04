# services/site_setting.py

from sqlalchemy.orm import Session
from models.site_setting import SiteSetting
from fastapi import HTTPException
from functools import lru_cache


_settings_cache: SiteSetting | None = None


def get_settings(db: Session) -> SiteSetting:
    global _settings_cache

    if _settings_cache is not None:
        return _settings_cache

    settings = db.query(SiteSetting).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not initialized")

    _settings_cache = settings
    return _settings_cache


def invalidate_settings_cache():
    global _settings_cache
    _settings_cache = None


def update_settings(db: Session, data):
    settings = db.query(SiteSetting).first()

    if not settings:
        raise HTTPException(status_code=404, detail="Settings not initialized")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(settings, key, value)

    db.commit()
    db.refresh(settings)
    invalidate_settings_cache()

    return settings
