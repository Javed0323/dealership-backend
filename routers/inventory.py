from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Security,
    Request,
    UploadFile,
    File,
)
from sqlalchemy.orm import Session, selectinload
from database import get_db
from models.car import Car
from schemas import InventoryCreate, InventoryBase, InventoryUpdate, InventoryOut
from security import get_verified_admin
from models import Inventory, Sale
import csv
import io
from datetime import datetime


router = APIRouter(
    prefix="/inventories",
    tags=["inventories"],
)


# Customer — only available units
@router.get("/{unit_id}", response_model=InventoryOut)
def get_inventory_unit(unit_id: int, db: Session = Depends(get_db)):
    unit = (
        db.query(Inventory)
        .options(selectinload(Inventory.car), selectinload(Inventory.media))
        .filter(Inventory.id == unit_id, Inventory.status == "available")  # ← guard
        .first()
    )
    if not unit:
        raise HTTPException(404, detail="Unit not found")
    return unit


# Admin — any status
@router.get("/admin/{unit_id}", response_model=InventoryOut)
def get_inventory_unit_admin(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user=Security(get_verified_admin),
):
    unit = (
        db.query(Inventory)
        .options(selectinload(Inventory.car), selectinload(Inventory.media))
        .filter(Inventory.id == unit_id)
        .first()
    )
    if not unit:
        raise HTTPException(404, detail="Unit not found")
    return unit


@router.post("/bulk-upload/{car_id}")
async def bulk_upload_inventory(
    car_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Security(get_verified_admin),  # ← auth guard
):
    if not file.filename.endswith(".csv"):  # type:ignore
        raise HTTPException(status_code=400, detail="Only CSV files allowed")

    content = await file.read()
    csv_reader = csv.DictReader(io.StringIO(content.decode("utf-8")))

    # Strip whitespace from all keys/values defensively
    rows = [{k.strip(): v.strip() for k, v in row.items()} for row in csv_reader]

    if not rows:
        raise HTTPException(status_code=400, detail="CSV file is empty")

    # Fetch all existing VINs in one query instead of one per row
    incoming_vins = {row.get("vin") for row in rows if row.get("vin")}
    existing_vins = {
        vin
        for (vin,) in db.query(Inventory.vin)
        .filter(Inventory.vin.in_(incoming_vins))
        .all()
    }

    created = 0
    skipped = 0
    errors = []
    new_inventories = []

    for index, row in enumerate(rows, start=1):
        vin = row.get("vin")
        purchase_price = row.get("purchase_price")
        registration_number = row.get("registration_number")
        color = row.get("color")

        if not vin or not purchase_price or not registration_number or not color:
            errors.append(f"Row {index}: Missing required field(s)")
            skipped += 1
            continue

        if vin in existing_vins:
            errors.append(f"Row {index}: VIN already exists ({vin})")
            skipped += 1
            continue

        try:
            new_inventories.append(
                Inventory(
                    car_id=car_id,
                    vin=vin,
                    purchase_price=float(purchase_price),
                    registration_number=registration_number,
                    color=color,
                    purchased_at=datetime.utcnow(),
                    status="available",
                )
            )
            existing_vins.add(vin)  # guard against duplicate VINs within the same CSV
            created += 1
        except ValueError:
            errors.append(
                f"Row {index}: Invalid purchase_price value ({purchase_price})"
            )
            skipped += 1

    # Single bulk insert instead of one db.add() per row
    if new_inventories:
        db.bulk_save_objects(new_inventories)
        db.commit()

    return {
        "message": "Bulk upload completed",
        "created": created,
        "skipped": skipped,
        "errors": errors,
    }


@router.post("/")
def add_inventory(
    item: InventoryCreate,
    db: Session = Depends(get_db),
    current_user=Security(get_verified_admin),  # ← auth guard
):
    # check duplicate VIN
    existing = db.query(Inventory).filter(Inventory.vin == item.vin).first()
    if existing:
        raise HTTPException(status_code=400, detail="VIN already exists")

    # check car exists
    car = db.query(Car).filter(Car.id == item.car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    inventory = Inventory(**item.model_dump(exclude_unset=True))
    db.add(inventory)
    db.commit()
    db.refresh(inventory)
    return inventory


# Public — customers, only available
@router.get("/", response_model=list[InventoryOut])
def get_inventories(db: Session = Depends(get_db)):
    units = (
        db.query(Inventory)
        .options(selectinload(Inventory.car), selectinload(Inventory.media))
        .filter(Inventory.status == "available")
        .all()
    )
    for u in units:
        print(u.media)
    return units


# Admin — all statuses, protected
@router.get("/admin/", response_model=list[InventoryOut])
def get_all_inventories(
    db: Session = Depends(get_db),
    current_user=Security(get_verified_admin),  # ← auth guard
):
    units = (
        db.query(Inventory)
        .options(selectinload(Inventory.car), selectinload(Inventory.media))
        .all()
    )
    return units


@router.patch("/{inventory_id}", response_model=InventoryBase)
def update_inventory(
    inventory_id: int,
    inventory_update: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user=Security(get_verified_admin),  # ← auth guard
):
    db_inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not db_inventory:
        raise HTTPException(status_code=404, detail="inventory not found")

    # check duplicate VIN
    existing = (
        db.query(Inventory)
        .filter(Inventory.vin == inventory_update.vin, Inventory.id != inventory_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="VIN already exists")

    # check car exists
    car = db.query(Car).filter(Car.id == inventory_update.car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    # check status
    if db_inventory.status == "sold":  # type:ignore
        raise HTTPException(status_code=400, detail="car is already sold")

    update_data = inventory_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_inventory, key, value)

    db.commit()
    db.refresh(db_inventory)
    return db_inventory


@router.delete("/{inventory_id}")
def delete_inventory(
    inventory_id: int,
    db: Session = Depends(get_db),
    current_user=Security(get_verified_admin),  # ← auth guard
):
    db_inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not db_inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    has_sales = db.query(Sale).filter(Sale.inventory_id == inventory_id).first()
    if has_sales:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete inventory with existing sales records",
        )
    db.delete(db_inventory)
    db.commit()
    return {"message": "Car deleted successfully"}
