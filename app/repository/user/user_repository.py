from prisma import Prisma
from prisma.models import User

from app.repository.user.dto import CreateUserDTO


class UserRepository():
    def __init__(self, db: Prisma):
        self.db = db

    async def create_user(self, data: CreateUserDTO) -> User:
        return await self.db.user.create(data={
            "email": data.email,
            "first_name": data.first_name,
            "last_name": data.last_name,
            "hashed_password": data.hashed_password,
        })

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.db.user.find_first(where={
            "email": email,
        })
