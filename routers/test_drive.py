from fastapi import APIRouter, Depends, HTTPException, Query, Security
from sqlalchemy.orm import Session
from database import get_db
import models
from models.test_drive import TestDrive
from schemas.test_drive import TestDriveCreate, TestDriveUpdate, TestDriveBase
from security import get_verified_user
from services.utils import get_or_404

router = APIRouter(
    dependencies=[Security(get_verified_user)],
    prefix="/test_drives",
    tags=["test_drives"],
)


@router.get("/")
def get_test_drives(db: Session = Depends(get_db)):
    db_test_drives = db.query(TestDrive).all()
    if not db_test_drives:
        raise HTTPException(status_code=404, detail="No test drives found")
    return db_test_drives


@router.post("/", response_model=TestDriveCreate)
def create_test_drive(
    test_drive: TestDriveCreate,
    db: Session = Depends(get_db),
):
    get_or_404(db, models.Inventory, test_drive.inventory_id, field="id")
    db_test_drive = TestDrive(**test_drive.model_dump())
    db.add(db_test_drive)
    db.commit()
    db.refresh(db_test_drive)
    return db_test_drive


@router.get("/{test_drive_id}", response_model=TestDriveBase)
def get_test_drive(
    test_drive_id: int,
    db: Session = Depends(get_db),
):
    db_test_drive = db.query(TestDrive).filter(TestDrive.id == test_drive_id).first()
    if not db_test_drive:
        raise HTTPException(status_code=404, detail="Test drive not found")
    return db_test_drive


@router.patch("/{test_drive_id}", response_model=TestDriveUpdate)
def update_test_drive(
    test_drive_id: int,
    test_drive_update: TestDriveUpdate,
    db: Session = Depends(get_db),
):
    db_test_drive = db.query(TestDrive).filter(TestDrive.id == test_drive_id).first()
    if not db_test_drive:
        raise HTTPException(status_code=404, detail="Test drive not found")

    get_or_404(db, models.Inventory, test_drive_update.inventory_id, field="id")
    if db_test_drive.status != "pending":  # type:ignore
        raise HTTPException(status_code=400, detail="Test drive already completed")
    updated_data = test_drive_update.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(db_test_drive, key, value)
    db.commit()
    db.refresh(db_test_drive)
    return db_test_drive


@router.delete("/{test_drive_id}")
def delete_test_drive(
    test_drive_id: int,
    db: Session = Depends(get_db),
):
    db_test_drive = db.query(TestDrive).filter(TestDrive.id == test_drive_id).first()
    if not db_test_drive:
        raise HTTPException(status_code=404, detail="Test drive not found")
    db.delete(db_test_drive)
    db.commit()
    return {"detail": "Test drive deleted successfully"}
