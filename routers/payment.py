from fastapi import APIRouter, Depends, HTTPException, Query, Security
from sqlalchemy.orm import Session
from database import get_db
import models
from models.payment import Payment
from schemas.payment import PaymentCreate, PaymentUpdate, PaymentBase
from security import get_verified_admin
from services.utils import get_or_404

router = APIRouter(
    dependencies=[Security(get_verified_admin)], prefix="/payments", tags=["payments"]
)


@router.get("/")
def get_payments(
    db: Session = Depends(get_db),
):
    db_payments = db.query(Payment).all()
    if not db_payments:
        raise HTTPException(status_code=404, detail="No Payments found")
    return db_payments


@router.post("/", response_model=PaymentCreate)
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
):
    try:
        sale = get_or_404(db, models.Sale, payment.sale_id, field="id")
        if not sale:
            raise HTTPException(status_code=404, detail="Sale not found")
        if payment.amount < 1000:  # Example validation: Minimum payment amount
            raise HTTPException(
                status_code=400, detail="Payment amount must be greater than 1000"
            )
        db_payment = Payment(**payment.model_dump())
        db.add(db_payment)
        if payment.amount >= sale.sale_price:
            sale.payment_status = "paid"  # Mark sale as paid if payment covers total
        db.commit()
        db.refresh(db_payment)
        return db_payment
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{payment_id}", response_model=PaymentBase)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
):
    db_payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment Not found")
    return db_payment


@router.patch("/{payment_id}", response_model=PaymentUpdate)
def update_payment(
    payment_id: int,
    payment_update: PaymentUpdate,
    db: Session = Depends(get_db),
):
    try:
        db_payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not db_payment:
            raise HTTPException(status_code=404, detail="Payment Not found")
        if (
            payment_update.amount is not None and payment_update.amount < 1000
        ):  # Example validation
            raise HTTPException(
                status_code=400, detail="Payment amount must be greater than 1000"
            )
        updated_data = payment_update.model_dump(exclude_unset=True)
        for key, value in updated_data.items():
            setattr(db_payment, key, value)
        if payment_update.amount >= db_payment.sale.sale_price:
            db_payment.sale.payment_status = (
                "paid"  # Update sale status if payment covers total
            )
        db.commit()
        db.refresh(db_payment)
        return db_payment
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{payment_id}")
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
):
    db_payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment Not found")
    db.delete(db_payment)
    db.commit()
    return {"Message": "Payment deleted successfully"}
