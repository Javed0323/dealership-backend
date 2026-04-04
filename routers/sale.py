from fastapi import APIRouter, Depends, HTTPException, Query, Security
from sqlalchemy.orm import Session
from database import get_db
import models
from models.sale import Sale
from schemas.sale import SaleCreate, SaleUpdate, SaleBase
from security import get_verified_admin
from services.utils import get_or_404

router = APIRouter(
    dependencies=[Security(get_verified_admin)], prefix="/sales", tags=["sales"]
)


@router.get("/")
def get_sales(db: Session = Depends(get_db)):
    db_sales = db.query(Sale).all()
    if not db_sales:
        raise HTTPException(status_code=404, detail="No Sales found")
    return db_sales


@router.post("/", response_model=SaleBase)
def create_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db),
):
    try:
        inventory = get_or_404(db, models.Inventory, sale.inventory_id, field="id")
        if inventory.status != "available":
            raise HTTPException(status_code=400, detail="Car is not available for sale")
        if sale.sale_status == "completed" and sale.payment_status != "paid":
            raise HTTPException(
                status_code=400, detail="Cannot complete sale until payment is paid"
            )
        if sale.sale_price < 0:
            raise HTTPException(
                status_code=400, detail="Sale price cannot be negative."
            )

        if sale.sale_price <= 100:
            raise HTTPException(
                status_code=400, detail="sale Price must be greater than 100."
            )
        db_sale = Sale(**sale.model_dump(exclude_unset=True))
        db.add(db_sale)
        # update inventory availability
        if sale.payment_status == "paid":
            inventory.status = "sold"
        else:
            inventory.status = "reserved"
        db.commit()
        db.refresh(db_sale)
        return db_sale
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{sale_id}", response_model=SaleBase)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
):
    db_sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not db_sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return db_sale


@router.patch("/{sale_id}", response_model=SaleUpdate)
def update_sale(
    sale_id: int,
    sale_update: SaleUpdate,
    db: Session = Depends(get_db),
):
    try:
        db_sale = db.query(Sale).filter(Sale.id == sale_id).first()
        if not db_sale:
            raise HTTPException(status_code=404, detail="Sale not found")
        if db_sale.sale_status == "completed":  # type: ignore
            raise HTTPException(
                status_code=400, detail="Completed sales cannot be modified!"
            )

        if (
            sale_update.sale_status == "completed"
            and sale_update.payment_status != "paid"
        ):
            raise HTTPException(
                status_code=400, detail="Cannot complete sale until payment is paid"
            )

        if sale_update.sale_price is not None:
            if sale_update.sale_price < 0:
                raise HTTPException(
                    status_code=400, detail="Sale price cannot be negative."
                )
            if sale_update.sale_price <= 100:
                raise HTTPException(
                    status_code=400, detail="sale Price must be greater than 100."
                )
        updated_data = sale_update.model_dump(exclude_unset=True)
        for key, value in updated_data.items():
            setattr(db_sale, key, value)
        db.commit()
        db.refresh(db_sale)
        return db_sale
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{sale_id}")
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
):
    db_sale = db.query(Sale).filter(Sale.id == sale_id).first()

    if not db_sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    # Prevent deleting completed sales
    if db_sale.sale_status == "completed":  # type:ignore
        raise HTTPException(status_code=400, detail="Completed sales cannot be deleted")

    # Release inventory
    inventory = (
        db.query(models.Inventory)
        .filter(models.Inventory.id == db_sale.inventory_id)
        .first()
    )

    if inventory:
        inventory.status = "available"  # type:ignore

    db.delete(db_sale)
    db.commit()

    return {"message": "Sale deleted successfully"}
