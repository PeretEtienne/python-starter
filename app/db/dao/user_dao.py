from dataclasses import dataclass
from typing import Optional, Protocol, cast

from argon2 import PasswordHasher
from sqlalchemy import Column, select
from sqlalchemy.exc import NoResultFound

from app.db.dao.abstract_dao import AbstractDAO, DAOProtocol
from app.db.models.user_model import User


class UserDAOProtocol(
    DAOProtocol[
        User, "UserCreate", "UserUpdatePassword",
    ], Protocol,
):
    async def get_by_email(self, email: str) -> Optional[User]: ...
    async def patch_password(self, user_id: int, password: str) -> None: ...

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
            key=user_id,
            updates=UserUpdatePassword(
                hashed_password=hashed_password,
                updated_by=user_id,  # Assuming the user is updating their own password
            ),
        )


@dataclass
class UserCreate:  # Handled by fastapi_users
    created_by: int


@dataclass
class UserUpdatePassword:
    hashed_password: str
    updated_by: int
