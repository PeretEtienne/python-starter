import logging

from fastapi import Depends, FastAPI, HTTPException, Response, status
from prisma import Prisma
from prisma.models import User
from pydantic import ValidationError

from app.dependencies.auth_dependencies import current_active_user
from app.dependencies.db import get_db_session
from app.repository.user_repository.user_repository import UserRepository
from app.services.auth_service.auth_service import AuthService
from app.services.auth_service.errors import (
    UserAlreadyExistsError,
)
from app.settings import settings
from app.web.api.auth.schemas import (
    RegisterPayloadSchema,
    RegisterResponse,
)

logger = logging.getLogger(settings.logger_name)

app = FastAPI()

router = app.router


def get_auth_service(db: Prisma = Depends(get_db_session)) -> AuthService:
    repository = UserRepository(db)
    return AuthService(repository)

@app.patch(
    "/users/me/password",
    tags=["auth"],
    summary="User: Patch Password",
    name="user:patch_password",
    response_class=Response,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def patch_user_password(
    updates: UserPasswordUpdate,
    service: AuthService = Depends(get_auth_service),
    user: User = Depends(current_active_user),
) -> None:
    """Patch user password."""

    try:
        if not PasswordHasher().verify(user.hashed_password, updates.old_password):
            raise Exception
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from e

    await user_dao.patch_password(user.id, updates.new_password)


@app.post(
    "/auth/register",
    tags=["auth"],
    summary="Register",
    name="auth:register",
    response_model=RegisterResponse,
)
async def register(
    payload: RegisterPayloadSchema,
    service: AuthService = Depends(get_auth_service),
) -> User:
    try:
        user = await service.register(
            email=payload.email,
            first_name=payload.first_name,
            last_name=payload.last_name,
            password=payload.password,
        )
    except (UserAlreadyExistsError, ValidationError) as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e

    return user
