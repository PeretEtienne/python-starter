from argon2 import PasswordHasher
from pydantic import ValidationError

from app.db.dao.user_dao import UserDAO
from app.db.models.user_model import User
from app.errors import DomainError
from app.services.user.errors import ChangePasswordError
from app.services.user.schemas import ValidatePasswordSchema


class UserService:
    def __init__(self, *, user_dao: UserDAO) -> None:
        self.user_dao = user_dao

    async def change_password(
        self,
        *,
        user: User,
        old_password: str,
        new_password: str,
    ) -> None:
        try:
            PasswordHasher().verify(user.hashed_password, old_password)
        except Exception as e:
            raise DomainError(
                detail={
                    "code": ChangePasswordError.INVALID_OLD_PASSWORD,
                    "message": "Old password is invalid",
                },
            ) from e

        try:
            schema = ValidatePasswordSchema.model_validate({"password": new_password})
        except ValidationError as e:
            raise DomainError(
                detail={
                    "code": ChangePasswordError.INVALID_NEW_PASSWORD,
                    "message": "New password does not meet the requirements.",
                },
            ) from e

        await self.user_dao.patch_password(
            user_id=user.id,
            password=schema.password,
        )
