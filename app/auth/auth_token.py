from typing import Any

from fastapi_users.authentication import JWTStrategy
from fastapi_users.jwt import decode_jwt, generate_jwt

from app.db.models.user_model import User
from app.settings import settings

SECRET = settings.auth_secret
LIFETIME_SECONDS = settings.auth_lifetime_seconds
REFRESH_SECONDS = settings.auth_refresh_seconds


def get_jwt_strategy() -> JWTStrategy[User, int]:
    return JWTStrategy(secret=SECRET, lifetime_seconds=LIFETIME_SECONDS)


def get_refresh_jwt_strategy() -> JWTStrategy[User, int]:
    return JWTStrategy(secret=SECRET, lifetime_seconds=REFRESH_SECONDS)


def generate_token(user_id: int, refresh: bool = False) -> str:
    strategy = get_refresh_jwt_strategy() if refresh else get_jwt_strategy()
    data = {"sub": str(user_id), "aud": strategy.token_audience}
    return generate_jwt(
        data,
        str(strategy.encode_key),
        strategy.lifetime_seconds,
        algorithm=strategy.algorithm,
    )


def decode_token(token: str) -> dict[str, Any]:
    strategy = get_jwt_strategy()
    return decode_jwt(
        token,
        str(strategy.decode_key),
        strategy.token_audience,
        algorithms=[strategy.algorithm],
    )
