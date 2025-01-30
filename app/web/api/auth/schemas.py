from typing import Literal
from pydantic import BaseModel, EmailStr


class RegisterPayloadSchema(BaseModel):
    """Register payload schema."""

    first_name: str
    last_name: str
    email: EmailStr
    password: str


class TokensSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"


class RefreshPayloadSchema(BaseModel):
    """Refresh payload schema."""

    refresh_token: str


class ForgotPasswordPayloadSchema(BaseModel):
    """Forgot password payload schema."""

    email: EmailStr


class ResetPasswordPayloadSchema(BaseModel):
    """Reset password payload schema."""

    token: str
    password: str
