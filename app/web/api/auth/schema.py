from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.consts import Permission
from app.services.user.schemas import validate_password


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

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password(value)

    model_config = ConfigDict(
        extra="ignore",
    )
