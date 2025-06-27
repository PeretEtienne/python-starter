from typing import Any, Optional, cast

from argon2 import PasswordHasher
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, select
from sqlalchemy.exc import NoResultFound

from app.consts import Permission
from app.db.dao.abstract_dao import AbstractDAO
from app.db.models.user_model import User


class UserDAO(AbstractDAO[User, "UserCreate", "UserUpdatePassword"]):
    model = User

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(self.model).where(cast(Column[str], self.model.email) == email)

        try:
            raw_model = await self.session.execute(query)
            return raw_model.scalar_one()
        except NoResultFound:
            return None

    async def patch_password(self, user_id: int, password: str) -> None:
        """Patch user password."""
        hashed_password = PasswordHasher().hash(password)

        await self.update(
            user_id,
            UserUpdatePassword(
                hashed_password=hashed_password,
            ),
        )


class UserCreate(BaseModel):
    def create_update_dict(self) -> dict[str, Any]:
        return self.model_dump(
            exclude_unset=True,
            exclude={
                "id",
                "is_active",
                "is_verified",
            },
        )

    first_name: str
    last_name: str
    email: EmailStr
    password: str
    permissions: list[Permission] = []


class UserUpdatePassword(BaseModel):
    hashed_password: str
