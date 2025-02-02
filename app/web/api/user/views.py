import logging
from typing import Any

from fastapi import Depends, FastAPI
from prisma.models import User

from app.dependencies.user import get_current_user
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
    user: User = Depends(get_current_user),
) -> Any:
    """Get current user."""

    return user
