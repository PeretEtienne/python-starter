from pydantic import BaseModel

from app.schemas import UserSchema


# GET /users/me
class GetMeResponse(UserSchema):
    pass

# PATCH /users/me/password
class UpdatePasswordPayloadSchema(BaseModel):
    old_password: str
    new_password: str
