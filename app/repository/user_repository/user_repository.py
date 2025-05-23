from prisma import Prisma
from prisma.models import User


class UserRepository():
    def __init__(self, db: Prisma) -> None:
        self.db = db

    async def get(self, user_id: int) -> User | None:
        return await self.db.user.find_first(where={"id": user_id})

    async def create_user(
        self, *,
        email: str, first_name: str, last_name: str, hashed_password: str,
    ) -> User:
        return await self.db.user.create(data={
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "hashed_password": hashed_password,
        })

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.db.user.find_first(where={
            "email": email,
        })

    async def update_user_refresh_token(
        self,
        user_id: int,
        refresh_token: str,
    ) -> User | None:
        return await self.db.user.update(
            where={
                "id": user_id,
            },
            data={
                "refresh_token": refresh_token,
            },
        )

    async def update_user_reset_token(
        self,
        user_id: int,
        reset_token: str | None,
    ) -> User | None:
        return await self.db.user.update(
            where={
                "id": user_id,
            },
            data={
                "reset_token": reset_token,
            },
        )

    async def update_user_password(
        self,
        user_id: int,
        hashed_password: str,
    ) -> User | None:
        return await self.db.user.update(
            where={
                "id": user_id,
            },
            data={
                "hashed_password": hashed_password,
            },
        )
