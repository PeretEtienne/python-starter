from pydantic import BaseModel, ConfigDict, EmailStr


class UserSchema(BaseModel):
    """User schema."""

    id: int
    first_name: str
    last_name: str
    email: EmailStr
    is_active: bool = True

# GET /users/me
class GetMeResponse(UserSchema):
    pass

# PATCH /users/me/password
class UpdatePasswordPayloadSchema(BaseModel):
    old_password: str
    new_password: str

class UserRead(BaseModel):
    """User read schema."""

    id: int
    first_name: str
    last_name: str
    email: EmailStr
    is_active: bool = True
    permissions: list[str]

    model_config = ConfigDict(from_attributes=True)


class RefreshPayload(BaseModel):
    """Refresh token payload schema."""

    refresh_token: str
