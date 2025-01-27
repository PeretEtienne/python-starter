from pydantic import BaseModel, EmailStr


class UserRead(BaseModel):
    """User read schema."""

    id: int
    first_name: str
    last_name: str
    email: EmailStr
    is_active: bool = True


class RegisterPayloadSchema(BaseModel):
    """Register payload schema."""

    first_name: str
    last_name: str
    email: EmailStr
    password: str
