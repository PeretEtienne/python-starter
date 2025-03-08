import logging

from fastapi import Depends, FastAPI, HTTPException, Response, status
from prisma import Prisma
from prisma.models import Post, User

from app.dependencies.db import get_db_session
from app.dependencies.user import get_current_user
from app.repository.post_repository.post_repository import PostRepository
from app.repository.user_repository.user_repository import UserRepository
from app.services.post_service.dto import PostCreateDTO, PostUpdateDTO
from app.services.post_service.errors import NotAuthorizedPatchPostError, PostNotFoundError
from app.services.post_service.post_service import PostService
from app.settings import settings
from app.web.api.post.schemas import CreatePostPayloadSchema, PatchPostPayloadSchema

logger = logging.getLogger(settings.logger_name)

app = FastAPI()

router = app.router


def get_post_service(db: Prisma = Depends(get_db_session)) -> PostService:
    post_reposiroty = PostRepository(db)
    user_repository = UserRepository(db)
    return PostService(
        post_repo=post_reposiroty,
        user_repo=user_repository,
    )


@app.post(
    "/posts",
    tags=["posts"],
    summary="Create Post",
    name="create:post",
)
async def create_post(
    data: CreatePostPayloadSchema,
    user: User = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service),
) -> Response:
    await post_service.create_post(user.id, PostCreateDTO(
        title=data.title,
        content=data.content,
        published=data.published,
        user_id=user.id,
    ))
    return Response(status_code=status.HTTP_201_CREATED)


@app.get(
    "/posts/{post_id}",
    tags=["posts"],
    summary="Get Post",
    name="get:post",
)
async def get_post(
    post_id: int,
    post_service: PostService = Depends(get_post_service),
    user: User = Depends(get_current_user),
) -> Post:
    try:
        post = await post_service.get_post(post_id)
    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e),
        ) from e

    return post


@app.patch(
    "/posts/{posts_id}",
    tags=["posts"],
    summary="Path: Post",
    name="patch:post",
)
async def patch_post(
    post_id: int,
    updates: PatchPostPayloadSchema,
    user: User = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service),
) -> None:
    """Get current user."""

    try:
        await post_service.patch_post(user, post_id, PostUpdateDTO(
            title=updates.title,
            content=updates.content,
        ))
    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e),
        ) from e
    except NotAuthorizedPatchPostError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e),
        ) from e
