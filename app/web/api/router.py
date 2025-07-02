from fastapi.routing import APIRouter

from app.web.api import auth, post, user

api_router = APIRouter()

api_router.include_router(user.router)
api_router.include_router(auth.router)
api_router.include_router(post.router)
