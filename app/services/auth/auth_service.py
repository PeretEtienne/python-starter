from datetime import timedelta
from prisma.models import User
from app.repository.user.dto import CreateUserDTO
from app.repository.user.user_repository import UserRepository
from app.services.auth.dto import RegisterData, Tokens
from app.services.auth.errors import InvalidCredentials, UserAlreadyExists
from app.settings import settings
from app.utils.security import create_access_token, decode_token, hash_password, verify_password


class AuthService():
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository

    async def register(self, data: RegisterData) -> User:
        exists = await self.user_repo.get_user_by_email(data.email)

        if exists:
            raise UserAlreadyExists('User already exists')

        return await self.user_repo.create_user(CreateUserDTO(
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
            hashed_password=hash_password(data.password),
        ))

    async def login(self, email: str, password: str) -> Tokens:
        user = await self.user_repo.get_user_by_email(email)

        if not user:
            print('no user')
            raise InvalidCredentials('Invalid credentials')

        if not verify_password(user.hashed_password, password):
            raise InvalidCredentials('Invalid credentials')

        access_token_expires = timedelta(
            seconds=settings.auth_lifetime_seconds
        )
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )

        refresh_token_expires = timedelta(seconds=settings.auth_refresh_seconds)
        refresh_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=refresh_token_expires
        )

        await self.user_repo.update_user_refresh_token(user.id, refresh_token)

        return Tokens(access_token=access_token, refresh_token=refresh_token)

    async def refresh(self, refresh_token: str) -> Tokens:
        try:
            user_id_str = decode_token(refresh_token).get("sub")
        except Exception:
            raise InvalidCredentials("Invalid refresh token")

        if not user_id_str:
            raise InvalidCredentials("Invalid refresh token")

        user_id = int(user_id_str)

        user = await self.user_repo.get(user_id)

        if not user or user.refresh_token != refresh_token:
            raise InvalidCredentials("Invalid refresh token")

        access_token_expires = timedelta(
            seconds=settings.auth_lifetime_seconds
        )
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )

        refresh_token_expires = timedelta(seconds=settings.auth_refresh_seconds)
        refresh_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=refresh_token_expires
        )

        await self.user_repo.update_user_refresh_token(user.id, refresh_token)

        return Tokens(access_token=access_token, refresh_token=refresh_token)
