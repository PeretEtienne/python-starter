import hashlib
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_users.db import SQLAlchemyUserDatabase

from app.auth.auth_backend import BearerResponseRefresh
from app.auth.auth_token import decode_token, generate_token
from app.consts import Permission
from app.db.dao.user_dao import UserCreate
from app.db.models.user_model import User
from app.dependencies.auth_dependencies import auth_backend_refresh, can, fastapi_users
from app.dependencies.db import get_user_db
from app.services.logger.service import Logger
from app.settings import settings
from app.web.api.user.schemas import RefreshPayload, UserRead

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend_refresh),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),  # type: ignore
    prefix="/auth",
    tags=["auth"],
    dependencies=[Depends(can(Permission.CREATE_USER))],
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/auth/refresh-token",
    tags=["auth"],
    summary="Auth:Jwt Refresh",
    name="auth:jwt.refresh",
    response_model=BearerResponseRefresh,
)
async def refresh_jwt_token(
    refresh_payload: RefreshPayload,
    user_db: SQLAlchemyUserDatabase[User, int] = Depends(get_user_db),
) -> Any:
    """Refresh JWT tokens.

    :todo: Remove when FastAPI Users supports refresh tokens.
    This function is a workaround for the absence of refresh token support in
    FastAPI Users : https://github.com/fastapi-users/fastapi-users/pull/1367
    """
    refresh_token = refresh_payload.refresh_token
    if not refresh_token:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Missing refresh token")

    decoded_token = decode_token(refresh_token)
    user_id = int(decoded_token["sub"])
    user = await user_db.get(user_id)

    if not user or not user.last_login:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid user")

    hasher = hashlib.sha3_256()
    hasher.update(refresh_token.encode())

    if hasher.hexdigest() != user.refresh_token:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid refresh token")

    if decoded_token["exp"] < int(datetime.now().timestamp()):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Refresh token expired")

    new_access_token = generate_token(user_id)
    new_refresh_token = generate_token(user_id, refresh=True)

    hasher = hashlib.sha3_256()
    hasher.update(new_refresh_token.encode())
    user.refresh_token = hasher.hexdigest()
    Logger.info(f"User {user.email} refreshed his tokens.")

    return BearerResponseRefresh(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type=settings.auth_token_type,
    )
