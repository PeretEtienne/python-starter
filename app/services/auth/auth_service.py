from datetime import datetime, timedelta, timezone

from prisma.models import User

from app.repository.user.dto import CreateUserDTO
from app.repository.user.user_repository import UserRepository
from app.services.auth.dto import RegisterData, Tokens
from app.services.auth.errors import (
    InvalidCredentialsError,
    TokenExpiredError,
    UserAlreadyExistsError,
    UserDoesNotExistError,
)
from app.settings import settings
from app.utils.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


class AuthService():
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repo = user_repository

    async def register(self, data: RegisterData) -> User:
        exists = await self.user_repo.get_user_by_email(data.email)

        if exists:
            raise UserAlreadyExistsError("User already exists")

        return await self.user_repo.create_user(CreateUserDTO(
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
            hashed_password=hash_password(data.password),
        ))

    async def login(self, email: str, password: str) -> Tokens:
        user = await self.user_repo.get_user_by_email(email)

        if not user:
            raise InvalidCredentialsError("Invalid credentials")

        if not verify_password(user.hashed_password, password):
            raise InvalidCredentialsError("Invalid credentials")

        access_token_expires = timedelta(
            seconds=settings.auth_lifetime_seconds,
        )
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires,
        )

        refresh_token_expires = timedelta(seconds=settings.auth_refresh_seconds)
        refresh_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=refresh_token_expires,
        )

        await self.user_repo.update_user_refresh_token(user.id, refresh_token)

        return Tokens(access_token=access_token, refresh_token=refresh_token)

    async def refresh(self, refresh_token: str) -> Tokens:
        try:
            decoded_token = decode_token(refresh_token)
        except Exception as e:
            raise InvalidCredentialsError("Invalid refresh token") from e

        exp = decoded_token.get("exp")
        if not exp or datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise TokenExpiredError("Token has expired")

        user_id_str = decoded_token.get("sub")
        if not user_id_str:
            raise InvalidCredentialsError("Invalid refresh token")

        user_id = int(user_id_str)

        user = await self.user_repo.get(user_id)

        if not user or user.refresh_token != refresh_token:
            raise InvalidCredentialsError("Invalid refresh token")

        access_token_expires = timedelta(
            seconds=settings.auth_lifetime_seconds,
        )
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires,
        )

        refresh_token_expires = timedelta(seconds=settings.auth_refresh_seconds)
        refresh_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=refresh_token_expires,
        )

        await self.user_repo.update_user_refresh_token(user.id, refresh_token)

        return Tokens(access_token=access_token, refresh_token=refresh_token)

    async def forgot_password(self, email: str) -> str:
        user = await self.user_repo.get_user_by_email(email)

        if not user:
            raise UserDoesNotExistError("User does not exist")

        reset_token_expires = timedelta(seconds=settings.auth_reset_seconds)
        reset_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=reset_token_expires,
        )

        await self.user_repo.update_user_reset_token(user.id, reset_token)

        return reset_token

    async def reset_password(
        self,
        reset_token: str,
        password: str,
    ) -> None:
        try:
            decoded_token = decode_token(reset_token)
        except Exception as e:
            raise InvalidCredentialsError("Invalid reset token") from e

        exp = decoded_token.get("exp")
        if not exp or datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise TokenExpiredError("Token has expired")

        user_id_str = decoded_token.get("sub")
        if not user_id_str:
            raise InvalidCredentialsError("Invalid refresh token")

        user_id = int(user_id_str)

        user = await self.user_repo.get(user_id)

        if not user or user.reset_token != reset_token:
            raise InvalidCredentialsError("Invalid reset token")

        await self.user_repo.update_user_password(user.id, hash_password(password))
        await self.user_repo.update_user_reset_token(user.id, None)
