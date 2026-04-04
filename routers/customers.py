from fastapi import APIRouter, Depends, HTTPException, Query, Security
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from security import get_verified_admin
from services.utils import get_or_404

router = APIRouter(
    dependencies=[Security(get_verified_admin)], prefix="/customer", tags=["customers"]
)


@router.get("/")
def get_customers(db: Session = Depends(get_db)):
    db_customers = db.query(models.Customer).all()
    if not db_customers:
        raise HTTPException(status_code=404, detail="No customers found")
    return db_customers


@router.post("/", response_model=schemas.Customer)
def create_customer(
    customer: schemas.CustomerCreate,
    db: Session = Depends(get_db),
):
    try:
        user_id = customer.user_id
        get_or_404(db, models.User, user_id, field="id")
        # one user can only be associated with one customer
        existing_customer = (
            db.query(models.Customer).filter(models.Customer.user_id == user_id).first()
        )
        if existing_customer:
            raise HTTPException(
                status_code=400, detail="User is already associated with a customer"
            )
        new_customer = models.Customer(**customer.model_dump())
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)
        return new_customer
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{customer_id}", response_model=schemas.Customer)
def read_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    db_customer = (
        db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    )
    if not db_customer:
        raise HTTPException(status_code=404, detail="customer not found!")
    return db_customer


@router.patch("/{customer_id}", response_model=schemas.Customer)
def update_customer(
    customer_id: int,
    customer_update: schemas.CustomerUpdate,
    db: Session = Depends(get_db),
):
    try:
        db_customer = (
            db.query(models.Customer).filter(models.Customer.id == customer_id).first()
        )
        if not db_customer:
            raise HTTPException(status_code=404, detail="customer not found")

        updated_data = customer_update.model_dump(exclude_unset=True)
        for key, value in updated_data.items():
            setattr(db_customer, key, value)
        db.commit()
        db.refresh(db_customer)
        return db_customer
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{customer_id}", response_model=schemas.Customer)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    db_customer = (
        db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    )
    if not db_customer:
        raise HTTPException(status_code=404, detail="customer not found")
    db.delete(db_customer)
    db.commit()
    return {"message": "Customer deleted successfully"}
