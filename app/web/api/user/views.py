from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dao.user_dao import UserDAO
from app.db.models.user_model import User
from app.dependencies.auth_dependencies import current_active_user
from app.dependencies.db import get_db_session
from app.errors import DomainError
from app.services.error_logger.service import Logger
from app.services.user.service import UserService
from app.web.api.user.schemas import GetMeResponse, UpdatePasswordPayloadSchema

router = APIRouter()


def get_user_service(db_session: AsyncSession = Depends(get_db_session)) -> UserService:
    dao = UserDAO(session=db_session)
    return UserService(user_dao=dao)


@router.get(
    "/users/me",
    tags=["users"],
    summary="User: Me",
    name="user:me",
    response_model=GetMeResponse,
)
async def get_me(
    user: User = Depends(current_active_user),
) -> Any:
    """Get current user."""

    return user


@router.patch(
    "/users/me/password",
    tags=["user"],
    summary="User: Patch Password",
    name="user:patch_password",
)
async def patch_user_password(
    updates: UpdatePasswordPayloadSchema,
    service: UserService = Depends(get_user_service),
    user: User = Depends(current_active_user),
) -> None:
    """Patch user password."""

    try:
        await service.change_password(
            user=user,
            old_password=updates.old_password,
            new_password=updates.new_password,
        )
    except DomainError as e:
        Logger.warning(e)
        raise HTTPException(**e.to_http_args()) from e
    except Exception as e:
        Logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
