from fastapi.routing import APIRouter

from app.web.api import (
    user
)

api_router = APIRouter()

api_router.include_router(user.router)
