from typing import Literal

from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    """User schema."""

    id: int
    first_name: str
    last_name: str
    email: EmailStr
    is_active: bool = True


class TokensSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
