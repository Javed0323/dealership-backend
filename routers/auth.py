from fastapi import APIRouter, Depends, HTTPException, Query, Security, Request
from sqlalchemy.orm import Session
from database import get_db
from security import (
    hash_password,
    verify_password,
    create_access_token,
    create_email_token,
    get_current_user,
)
from models.user import User
from fastapi.security import OAuth2PasswordRequestForm
import smtplib
from email.message import EmailMessage
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta
from schemas.user import UserCreate
import requests
import os
from fastapi import Form

from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.extension import Limiter as ExtLimiter

# For per-route limiter
from services.limiter import limiter  # import the limiter instance


router = APIRouter(prefix="/auth", tags=["auth"])

EMAIL = "j43430749@gmail.com"
SECRET_KEY = "xfygxlbajsjpaltk"

RecaptchaSecretKey = "6Ld06XssAAAAAJKTNkMtZXeVIsDqFd86pBNWNn2o"


@router.delete("/user/{user_id}")
def delete_user(
    user_id: int, db: Session = Depends(get_db), token=Security(get_current_user)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return {"error": "user not found!"}
    db.delete(db_user)
    db.commit()
    return {"message": "user deleted successfully"}


# -------- Register ---------
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    hashed_pw = hash_password(user.password)
    new_user = User(email=user.email, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send verification email
    token = create_email_token(new_user.email)  # type: ignore
    send_verification_email(new_user.email, token)  # type: ignore

    return {"message": "User created. Check your email to verify your account."}


# Optional reCAPTCHA verification
def verify_recaptcha(token: str):
    secret = RecaptchaSecretKey
    resp = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={"secret": secret, "response": token},
    ).json()
    return resp.get("success", False)


@router.post("/login")
@limiter.limit("5/minute")  # Apply rate limit to this route
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    recaptcha_token: str = Form(None),  # optional
):
    # Optional: verify reCAPTCHA
    if recaptcha_token:
        success = verify_recaptcha(recaptcha_token)
        if not success:
            raise HTTPException(status_code=400, detail="Invalid reCAPTCHA")

    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(form_data.password, str(user.password)):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Include role in token
    token = create_access_token({"user_id": user.id, "role": user.role})  # type: ignore

    return {"access_token": token, "token_type": "bearer"}


# -------- Send verification email ---------


def send_verification_email(to_email: str, token: str):
    msg = EmailMessage()
    msg["Subject"] = "Verify Your Email"
    msg["From"] = EMAIL
    msg["To"] = to_email

    verification_link = f"http://127.0.0.1:8000/auth/verify-email?token={token}"

    msg.set_content(f"Click this link to verify your email:\n{verification_link}")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, SECRET_KEY)
        server.send_message(msg)


# -------- Verify Email ---------


@router.get("/verify-email/")
def verify_email(token: str, db: Session = Depends(get_db)):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    if user.is_verified:  # type: ignore
        return {"message": "User already verified"}
    # get userName from email and update userName and is_verified in db
    if email and not user.username:  # type: ignore
        user.username = email.split("@")[0]
        user.is_verified = True  # type: ignore
        db.commit()

    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
def resend_verification(email: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:  # type: ignore
        return {"message": "User already verified"}

    # Optional: Simple rate limiting (1 request per minute)
    if hasattr(user, "last_verification_sent"):

        if user.last_verification_sent:  # type: ignore
            if (datetime.utcnow() - user.last_verification_sent).total_seconds() < 60:
                raise HTTPException(
                    status_code=429, detail="Please wait before requesting again"
                )

    # Create new JWT token
    expire = datetime.utcnow() + timedelta(minutes=15)
    token = jwt.encode(
        {"sub": user.email, "exp": expire}, SECRET_KEY, algorithm="HS256"
    )

    # Send verification email
    send_verification_email(user.email, token)  # type: ignore

    # Update last sent time
    user.last_verification_sent = datetime.utcnow()  # type: ignore
    db.commit()

    return {"message": "Verification email resent successfully"}


@router.get("/profile")
def profile(current_user=Depends(get_current_user)):
    return current_user
