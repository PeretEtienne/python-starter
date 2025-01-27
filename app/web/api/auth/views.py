import logging

from fastapi import Depends, FastAPI, HTTPException, status
from prisma import Prisma

from app.dependencies.db import get_db_session
from app.repository.user.user_repository import UserRepository
from app.services.auth.auth_service import AuthService
from app.services.auth.dto import RegisterData
from app.services.auth.errors import InvalidCredentials, UserAlreadyExists
from app.settings import settings
from app.web.api.auth.schemas import (LoginPayloadSchema, RegisterPayloadSchema, TokensSchema)

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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except Exception as e:
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
    payload: LoginPayloadSchema,
    service: AuthService = Depends(get_auth_service),
):
    try:
        credentials = await service.login(payload.email, payload.password)
    except InvalidCredentials as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    return credentials
