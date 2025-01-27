from argon2 import PasswordHasher
from datetime import datetime, timedelta, timezone

import jwt

from app.settings import settings


def hash_password(password: str) -> str:
    return PasswordHasher().hash(password)


def verify_password(hashed_password: str, password: str) -> bool:
    return PasswordHasher().verify(hashed_password, password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.auth_secret,
        algorithm="HS256"
    )
    return encoded_jwt


def decode_token(token: str):
    return jwt.decode(token, settings.auth_secret, algorithms=["HS256"])
