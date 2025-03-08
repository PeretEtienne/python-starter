from pydantic import BaseModel, EmailStr

from app.schemas import TokensSchema, UserSchema


# /auth/register
class RegisterPayloadSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class RegisterResponse(UserSchema):
    pass


# /auth/login
class LoginResponse(TokensSchema):
    pass


# /auth/refresh
class RefreshPayloadSchema(BaseModel):
    refresh_token: str


class RefreshResponse(TokensSchema):
    pass


# /auth/forgot-password
class ForgotPasswordPayloadSchema(BaseModel):
    email: EmailStr


# /auth/reset-password
class ResetPasswordPayloadSchema(BaseModel):
    token: str
    password: str
