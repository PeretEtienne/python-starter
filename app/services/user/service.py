from argon2 import PasswordHasher

from app.db.dao.user_dao import UserDAO
from app.db.models.user_model import User
from app.services.user.schemas import ValidatePasswordSchema


class UserService():
    def __init__(self, *, user_dao: UserDAO) -> None:
        self.user_dao = user_dao

    async def change_password(
        self, *,
        user: User, old_password: str, new_password: str,
    ) -> None:
        try:
            PasswordHasher().verify(user.hashed_password, old_password)
        except Exception as e:
            raise ValueError("Old password is incorrect") from e

        schema = ValidatePasswordSchema.model_validate({"password": new_password})
        await self.user_dao.patch_password(
            user_id=user.id, password=schema.password,
        )
