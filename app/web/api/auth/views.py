import logging
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from prisma import Prisma

from app.dependencies.db import get_db_session
from app.repository.user.user_repository import UserRepository
from app.services.auth.auth_service import AuthService
from app.services.auth.dto import RegisterData
from app.services.auth.errors import InvalidCredentials, TokenExpired, UserAlreadyExists
from app.settings import settings
from app.web.api.auth.schemas import (RefreshPayloadSchema, RegisterPayloadSchema, TokensSchema)

logger = logging.getLogger(settings.logger_name)

app = FastAPI()

router = app.router


def get_auth_service(db: Prisma = Depends(get_db_session)) -> AuthService:
    repository = UserRepository(db)
    return AuthService(repository)


@app.post(
    "/auth/register",
    tags=["auth"],
    summary="Register",
    name="auth:register",
)
async def register(
    payload: RegisterPayloadSchema,
    service: AuthService = Depends(get_auth_service),
):
    try:
        user = await service.register(RegisterData(**payload.model_dump()))
    except UserAlreadyExists as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e

    return user


@app.post(
    "/auth/login",
    tags=["auth"],
    summary="Login",
    name="auth:login",
    response_model=TokensSchema,
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: AuthService = Depends(get_auth_service),
):
    try:
        credentials = await service.login(form_data.username, form_data.password)
    except InvalidCredentials as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    return credentials


@app.post(
    "auth/refresh",
    tags=["auth"],
    summary="Refresh",
    name="auth:refresh",
    response_model=TokensSchema,
)
async def refresh(
    payload: RefreshPayloadSchema,
    service: AuthService = Depends(get_auth_service),
):
    try:
        credentials = await service.refresh(payload.refresh_token)
    except (InvalidCredentials, TokenExpired) as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    return credentials
