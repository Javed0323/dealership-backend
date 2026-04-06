from fastapi import APIRouter, Depends, HTTPException, Security, Request
from sqlalchemy.orm import Session, selectinload
from database import get_db
from models.car import Car, CarEngine, CarDimensions, CarSafety, CarFeatures
from schemas import (
    CarCreate,
    CarUpdate,
    CarRead,
    CarEngineCreate,
    CarDimensionsCreate,
    CarSafetyCreate,
    CarFeaturesCreate,
)
from security import get_verified_admin
from services.query_utils import apply_pagination, apply_filters, apply_search, apply_sorting
from models import Inventory

router = APIRouter(
    dependencies=[Security(get_verified_admin)], prefix="/cars", tags=["cars"]
)


from models.car import Car, CarEngine, CarDimensions, CarSafety, CarFeatures
from sqlalchemy.orm import selectinload

RELATED_MODELS = {
    "engine": CarEngine,
    "dimensions": CarDimensions,
    "safety": CarSafety,
    "features": CarFeatures,
}

RESERVED = {"sort", "limit", "offset"}


# do not guard this router since it's used for both public search and admin CRUD
publicRouter = APIRouter(prefix="/cars", tags=["cars"])
@publicRouter.get("/search")
def search_cars(
    request: Request,
    sort: str = None,  # type: ignore
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    filters = {k: v for k, v in request.query_params.items() if k not in RESERVED}
    search = filters.pop("search", None)

    joined = set()  # shared between filter + sort so we don't double-join

    car_load = selectinload(Inventory.car)

    query = (
        db.query(Inventory)
        .join(Inventory.car)
        .options(
            selectinload(Inventory.media),
            car_load.selectinload(Car.engine),
            car_load.selectinload(Car.dimensions),
            car_load.selectinload(Car.safety),
            car_load.selectinload(Car.features),
        )
        .filter(Inventory.status == "available")  # only available cars for customers
    )
    query = apply_search(query, search, Car, RELATED_MODELS, joined) # type: ignore

    query = apply_filters(query, Car, filters, RELATED_MODELS, joined)
    query = apply_sorting(query, Car, sort, RELATED_MODELS, joined)

    total = query.count()

    query = apply_pagination(query, limit, offset)

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": query.all(),
    }

# add a test endpoint to verify that the public router is working without auth
@publicRouter.get("/test")
def test_public_router(db: Session = Depends(get_db)):
    return {"message": "Public router is working", "car_count": db.query(Car).count()}

# ── Helpers ───────────────────────────────────────────────────────────────────


def get_car_or_404(car_id: int, db: Session) -> Car:
    car = (
        db.query(Car)
        .options(
            selectinload(Car.engine),
            selectinload(Car.dimensions),
            selectinload(Car.safety),
            selectinload(Car.features),
        )
        .filter(Car.id == car_id)
        .first()
    )
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


def upsert_nested(db: Session, model_cls, car_id: int, data: dict):
    """Update existing nested record or create it if it doesn't exist yet."""
    instance = db.query(model_cls).filter_by(car_id=car_id).first()
    if instance:
        for key, value in data.items():
            setattr(instance, key, value)
    else:
        instance = model_cls(car_id=car_id, **data)
        db.add(instance)
    return instance


# ── Cars ──────────────────────────────────────────────────────────────────────


@router.post("/", response_model=CarRead)
def create_car(car: CarCreate, db: Session = Depends(get_db)):
    # Extract nested data before creating the Car row
    engine_data = car.engine.model_dump() if car.engine else None
    dimensions_data = car.dimensions.model_dump() if car.dimensions else None
    safety_data = car.safety.model_dump() if car.safety else None
    features_data = car.features.model_dump() if car.features else None

    # Create core car
    db_car = Car(
        **car.model_dump(exclude={"engine", "dimensions", "safety", "features"})
    )
    db.add(db_car)
    db.flush()  # get db_car.id without committing

    # Create nested records if provided
    if engine_data:
        db.add(CarEngine(car_id=db_car.id, **engine_data))
    if dimensions_data:
        db.add(CarDimensions(car_id=db_car.id, **dimensions_data))
    if safety_data:
        db.add(CarSafety(car_id=db_car.id, **safety_data))
    if features_data:
        db.add(CarFeatures(car_id=db_car.id, **features_data))

    try:
        db.commit()
        return get_car_or_404(db_car.id, db)  # type: ignore
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
def get_cars(db: Session = Depends(get_db)):
    cars = db.query(Car).options(selectinload(Car.engine)).all()
    if not cars:
        raise HTTPException(status_code=404, detail="No cars found")
    return cars


@router.get("/{car_id}", response_model=CarRead)
def get_car(car_id: int, db: Session = Depends(get_db)):
    return get_car_or_404(car_id, db)


@router.patch("/{car_id}", response_model=CarRead)
def update_car(car_id: int, car_update: CarUpdate, db: Session = Depends(get_db)):
    db_car = get_car_or_404(car_id, db)

    # Update core fields only
    core_data = car_update.model_dump(
        exclude_unset=True, exclude={"engine", "dimensions", "safety", "features"}
    )
    for key, value in core_data.items():
        setattr(db_car, key, value)

    try:
        db.commit()
        return get_car_or_404(car_id, db)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{car_id}")
def delete_car(car_id: int, db: Session = Depends(get_db)):
    db_car = db.query(Car).filter(Car.id == car_id).first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Car not found")
    db.delete(db_car)
    db.commit()
    return {"message": "Car deleted successfully"}


# ── Nested sub-resources (edit mode only) ─────────────────────────────────────


@router.put("/{car_id}/engine", response_model=CarRead)
def upsert_engine(car_id: int, data: CarEngineCreate, db: Session = Depends(get_db)):
    get_car_or_404(car_id, db)  # ensure car exists
    upsert_nested(db, CarEngine, car_id, data.model_dump())
    try:
        db.commit()
        return get_car_or_404(car_id, db)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{car_id}/dimensions", response_model=CarRead)
def upsert_dimensions(
    car_id: int, data: CarDimensionsCreate, db: Session = Depends(get_db)
):
    get_car_or_404(car_id, db)
    upsert_nested(db, CarDimensions, car_id, data.model_dump())
    try:
        db.commit()
        return get_car_or_404(car_id, db)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{car_id}/safety", response_model=CarRead)
def upsert_safety(car_id: int, data: CarSafetyCreate, db: Session = Depends(get_db)):
    get_car_or_404(car_id, db)
    upsert_nested(db, CarSafety, car_id, data.model_dump())
    try:
        db.commit()
        return get_car_or_404(car_id, db)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{car_id}/features", response_model=CarRead)
def upsert_features(
    car_id: int, data: CarFeaturesCreate, db: Session = Depends(get_db)
):
    get_car_or_404(car_id, db)
    upsert_nested(db, CarFeatures, car_id, data.model_dump())
    try:
        db.commit()
        return get_car_or_404(car_id, db)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
