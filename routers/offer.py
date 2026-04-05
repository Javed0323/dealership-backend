from fastapi import APIRouter, Depends, HTTPException, Query, Security
from sqlalchemy.orm import Session
from database import get_db
import models
from models.offer import Offer
from schemas.offer import OfferCreate, OfferUpdate, OfferBase
from security import get_verified_admin
from services.utils import get_or_404

router = APIRouter(
    dependencies=[Security(get_verified_admin)], prefix="/offers", tags=["offers"]
)

# get active offers for customers (filter by inventory status = available)
publicRouter = APIRouter(prefix="/offers", tags=["offers"])
@publicRouter.get("/")
def get_offers_public(db: Session = Depends(get_db)):
    db_offers = (
        db.query(Offer)
        .join(models.Inventory)
        .filter(models.Inventory.status == "available")
        .all()
    )
    if not db_offers:
        raise HTTPException(status_code=404, detail="No offers found")
    return db_offers


@router.get("/admin/")
def get_offers(db: Session = Depends(get_db)):
    db_offers = db.query(Offer).all()
    if not db_offers:
        raise HTTPException(status_code=404, detail="No offers found")
    return db_offers


@router.post("/", response_model=OfferCreate)
def create_offer(
    offer: OfferCreate,
    db: Session = Depends(get_db),
):
    get_or_404(db, models.Inventory, offer.inventory_id, field="id")
    db_offer = Offer(**offer.model_dump())
    db.add(db_offer)
    db.commit()
    db.refresh(db_offer)
    return db_offer


@router.get("/{offer_id}", response_model=OfferBase)
def get_offer(
    offer_id: int,
    db: Session = Depends(get_db),
):
    db_offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not db_offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return db_offer


@router.patch("/{offer_id}", response_model=OfferUpdate)
def update_offer(
    offer_id: int,
    offer_update: OfferUpdate,
    db: Session = Depends(get_db),
):
    db_offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not db_offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    inventory = get_or_404(db, models.Inventory, offer_update.inventory_id, field="id")
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    updated_data = offer_update.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(db_offer, key, value)
    db.commit()
    db.refresh(db_offer)
    return db_offer


@router.delete("/{offer_id}")
def delete_offer(
    offer_id: int,
    db: Session = Depends(get_db),
):
    db_offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not db_offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    db.delete(db_offer)
    db.commit()
    return {"message": "Offer deleted successfully"}
