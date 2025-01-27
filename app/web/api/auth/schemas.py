from typing import Literal
from pydantic import BaseModel, EmailStr


class RegisterPayloadSchema(BaseModel):
    """Register payload schema."""

    first_name: str
    last_name: str
    email: EmailStr
    password: str


class LoginPayloadSchema(BaseModel):
    """Login payload schema."""

    email: EmailStr
    password: str


class TokensSchema(BaseModel):
    access_token: str
    refresh_token: str
    type: Literal["Bearer"] = "Bearer"


class RefreshPayloadSchema(BaseModel):
    """Refresh payload schema."""

    refresh_token: str
