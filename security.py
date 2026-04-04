from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from models.user import User

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

SECRET_KEY = "xfygxlbajsjpaltk"
ALGORITHM = "HS256"


def create_email_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=15)
    return jwt.encode({"sub": email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def verify_email_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("user_id")
    except JWTError as e:
        print("jwt error", e)
        return None


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=2)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401)
    except JWTError:
        raise HTTPException(status_code=401)

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401)
    return user


def get_verified_user(user: User = Depends(get_current_user)):
    if not user.is_verified:  # type: ignore
        raise HTTPException(status_code=403, detail="User not verified")
    return user


def get_verified_admin(user: User = Depends(get_verified_user)):
    if user.role != "admin":  # type: ignore
        raise HTTPException(status_code=403, detail="User is not an admin")
    return user
