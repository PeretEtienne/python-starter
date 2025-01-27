from prisma.models import User
from app.repository.user.dto import CreateUserDTO
from app.repository.user.user_repository import UserRepository
from app.services.auth.dto import RegisterData
from app.services.auth.errors import UserAlreadyExists


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
            hashed_password=data.password,
        ))
