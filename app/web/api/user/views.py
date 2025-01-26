import logging
from typing import Any

from fastapi import Depends, FastAPI
from prisma import Prisma

from app.dependencies.db import get_db_session
from app.settings import settings
from app.web.api.user.schemas import (
    UserRead,
)

logger = logging.getLogger(settings.logger_name)

app = FastAPI()

router = app.router


@app.get(
    "/users/me",
    tags=["users"],
    summary="User: Me",
    name="user:me",
    response_model=UserRead,
)
async def get_me(
    db: Prisma = Depends(get_db_session),
) -> Any:
    """Get current user."""

    return await db.user.find_first(
        where={
            "id": 1
        },
    )
