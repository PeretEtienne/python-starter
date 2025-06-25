import logging
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import ValidationError

from app.db.dao.user_dao import UserDAO
from app.db.models.user_model import User
from app.dependencies.auth_dependencies import current_active_user
from app.services.user.service import UserService
from app.settings import settings
from app.web.api.user.schemas import GetMeResponse, UpdatePasswordPayloadSchema

logger = logging.getLogger(settings.logger_name)

app = FastAPI()

router = app.router

def get_user_service() -> UserService:
    dao = UserDAO()
    return UserService(user_dao=dao)

@app.get(
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

@app.patch(
    "/users/me/password",
    tags=["auth"],
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
            new_passwoard=updates.new_password,
        )
    except (ValueError, ValidationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e) from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
