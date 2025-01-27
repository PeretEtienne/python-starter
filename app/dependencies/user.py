from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from prisma import Prisma
from prisma.models import User

from app.dependencies.db import get_db_session
from app.utils.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Prisma = Depends(get_db_session),
) -> User:
    user_id_str = decode_token(token).get("sub")

    if not user_id_str:
        raise HTTPException(status_code=400, detail="Invalid token")

    user_id = int(user_id_str)

    user = await db.user.find_first(where={
        "id": user_id,
        "is_active": True
    })

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
