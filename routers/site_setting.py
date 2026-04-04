# routers/site_settings.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas.site_setting import SiteSettingsResponse, SiteSettingsUpdate
from services.site_setting import get_settings, update_settings

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/", response_model=SiteSettingsResponse)
def read_settings(db: Session = Depends(get_db)):
    return get_settings(db)


@router.put("/", response_model=SiteSettingsResponse)
def edit_settings(payload: SiteSettingsUpdate, db: Session = Depends(get_db)):
    return update_settings(db, payload)
