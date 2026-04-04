# routers/dashboard.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas.dashboard import DashboardResponse
from services.dashboard import get_dashboard_data

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/", response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db)):
    return get_dashboard_data(db)
