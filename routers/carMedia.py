import os
import uuid
import boto3
from fastapi import APIRouter, Depends, HTTPException, Security, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
from models.car import Car
from models.car import CarMedia
from models import Inventory
from security import get_verified_admin

from dotenv import load_dotenv
import os
from pydantic import BaseModel

load_dotenv()

S3_BUCKET = os.getenv("S3_BUCKET_NAME")
S3_REGION = os.getenv("AWS_REGION")
CDN_BASE = os.getenv(
    "CDN_BASE_URL"
)  # e.g. https://cdn.yourdomain.com — falls back to S3 URL

s3 = boto3.client(
    "s3",
    region_name=S3_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4"}
ALLOWED_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def upload_to_s3(file: UploadFile, inventory_id: int) -> str:
    ext = file.filename.rsplit(".", 1)[-1].lower()  # type:ignore
    key = f"cars/{inventory_id}/{uuid.uuid4()}.{ext}"
    content = file.file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 50 MB limit")

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=content,
        ContentType=file.content_type,
    )

    if CDN_BASE:
        return f"{CDN_BASE.rstrip('/')}/{key}"
    return f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{key}"


def delete_from_s3(url: str):
    # Extract the S3 key from the stored URL
    try:
        if CDN_BASE:
            key = url.replace(CDN_BASE.rstrip("/") + "/", "")
        else:
            key = "/".join(url.split("/")[3:])  # strip bucket/domain prefix
        s3.delete_object(Bucket=S3_BUCKET, Key=key)
    except Exception:
        pass  # Don't block DB deletion if S3 fails — log in production


def get_car_or_404(inventory_id: int, db: Session) -> Inventory:
    inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory


def get_media_or_404(inventory_id: int, media_id: int, db: Session) -> CarMedia:
    media = (
        db.query(CarMedia)
        .filter(CarMedia.id == media_id, CarMedia.inventory_id == inventory_id)
        .first()
    )
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return media


# ── Mount these routes INSIDE your existing car router ────────────────────────
# Add to router.py: from .car_media import router as media_router
# Then: router.include_router(media_router)
# Or just paste these routes directly into your existing car router file.

media_router = APIRouter(
    dependencies=[Security(get_verified_admin)],
    prefix="/cars/{inventory_id}/media",
    tags=["car media"],
)


@media_router.get("/")
def get_car_media(
    inventory_id: int,
    db: Session = Depends(get_db),
):
    get_car_or_404(inventory_id, db)
    return db.query(CarMedia).filter(CarMedia.inventory_id == inventory_id).all()


@media_router.post("/", status_code=201)
async def upload_car_media(
    inventory_id: int,
    file: UploadFile = File(...),
    media_type: str = Form(...),  # "image" | "video" | "360"
    alt_text: str = Form(""),
    is_primary: bool = Form(False),
    db: Session = Depends(get_db),
):
    get_car_or_404(inventory_id, db)

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400, detail=f"Unsupported file type: {file.content_type}"
        )

    if media_type not in ("image", "video", "360"):
        raise HTTPException(
            status_code=400, detail="media_type must be image, video, or 360"
        )

    url = upload_to_s3(file, inventory_id)

    # If this is set as primary, demote all others first
    if is_primary:
        db.query(CarMedia).filter(
            CarMedia.inventory_id == inventory_id,
            CarMedia.media_type == "image",
        ).update({"is_primary": False})

    media = CarMedia(
        inventory_id=inventory_id,
        media_type=media_type,
        url=url,
        alt_text=alt_text or None,
        is_primary=is_primary,
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media


class CarMediaUpdate(BaseModel):
    alt_text: str | None = None


@media_router.patch("/{media_id}")
def update_car_media(
    inventory_id: int,
    media_id: int,
    data: CarMediaUpdate,
    db: Session = Depends(get_db),
):
    media = get_media_or_404(inventory_id, media_id, db)
    if data.alt_text is not None:
        media.alt_text = data.alt_text  # type: ignore
    db.commit()
    db.refresh(media)
    return media


@media_router.patch("/{media_id}/set-primary")
def set_primary_media(
    inventory_id: int,
    media_id: int,
    db: Session = Depends(get_db),
):
    get_car_or_404(inventory_id, db)
    media = get_media_or_404(inventory_id, media_id, db)

    if media.media_type != "image":  # type:ignore
        raise HTTPException(status_code=400, detail="Only images can be set as primary")

    # Demote all, then promote this one — single round trip
    db.query(CarMedia).filter(
        CarMedia.inventory_id == inventory_id,
        CarMedia.media_type == "image",
    ).update({"is_primary": False})

    media.is_primary = True  # type:ignore
    db.commit()
    db.refresh(media)
    return media


@media_router.delete("/{media_id}")
def delete_car_media(
    inventory_id: int,
    media_id: int,
    db: Session = Depends(get_db),
):
    media = get_media_or_404(inventory_id, media_id, db)

    delete_from_s3(media.url)  # type:ignore
    db.delete(media)
    db.commit()

    return {"message": "Media deleted"}
