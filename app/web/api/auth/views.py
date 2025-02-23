import logging
from typing import Annotated, Optional

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from prisma import Prisma
from prisma.models import User

from app.dependencies.db import get_db_session
from app.repository.user.user_repository import UserRepository
from app.services.auth.auth_service import AuthService
from app.services.auth.dto import RegisterUserInputDTO, TokensDTO
from app.services.auth.errors import (
    InvalidCredentialsError,
    TokenExpiredError,
    UserAlreadyExistsError,
    UserDoesNotExistError,
)
from app.settings import settings
from app.web.api.auth.schemas import (
    ForgotPasswordPayloadSchema,
    RefreshPayloadSchema,
    RegisterPayloadSchema,
    ResetPasswordPayloadSchema,
    TokensSchema,
)

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
) -> User:
    try:
        user = await service.register(RegisterUserInputDTO(
            email=payload.email,
            first_name=payload.first_name,
            last_name=payload.last_name,
            password=payload.password,
        ))
    except UserAlreadyExistsError as e:
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
) -> TokensDTO:
    try:
        credentials = await service.login(form_data.username, form_data.password)
    except InvalidCredentialsError as e:
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
) -> TokensDTO:
    try:
        credentials = await service.refresh(payload.refresh_token)
    except (InvalidCredentialsError, TokenExpiredError) as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    return credentials


@app.post(
    "/auth/forgot-password",
    tags=["auth"],
    summary="Forgot password",
    name="auth:forgot-password",
)
async def forgot_password(
    payload: ForgotPasswordPayloadSchema,
    service: AuthService = Depends(get_auth_service),
) -> Response:
    token: Optional[str] = None

    try:
        token = await service.forgot_password(payload.email)
    except UserDoesNotExistError:
        pass
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    # NOTE: You probably want to send email here

    if token:
        logger.info(f"Password reset token: {token}")
    else:
        logger.info("Password reset token not generated")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post(
    "/auth/reset-password",
    tags=["auth"],
    summary="Reset password",
    name="auth:reset-password",
)
async def reset_password(
    payload: ResetPasswordPayloadSchema,
    service: AuthService = Depends(get_auth_service),
) -> Response:

    try:
        await service.reset_password(payload.token, payload.password)
    except (InvalidCredentialsError, TokenExpiredError) as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    return Response(status_code=status.HTTP_204_NO_CONTENT)
