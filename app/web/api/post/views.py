from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dao.post_dao import PostDAO
from app.db.models.user_model import User
from app.dependencies.auth_dependencies import current_active_user
from app.dependencies.db import get_db_session
from app.errors import DomainError
from app.services.logger.service import Logger
from app.services.post.dto import PostCreateDTO
from app.services.post.service import PostService
from app.web.api.post.schemas import CreatePostPayloadSchema, CreatePostResponseSchema

router = APIRouter()


def get_post_service(db_session: AsyncSession = Depends(get_db_session)) -> PostService:
    dao = PostDAO(session=db_session)
    return PostService(post_dao=dao)


@router.post(
    "/posts",
    tags=["posts"],
    summary="Posts: Create",
    name="post:create",
    response_model=CreatePostResponseSchema,
)
async def create_post(
    payload: CreatePostPayloadSchema,
    user: User = Depends(current_active_user),
    service: PostService = Depends(get_post_service),
) -> CreatePostResponseSchema:
    """Get current user."""

    try:
        post_id = await service.create_post(
            data=PostCreateDTO(
                title=payload.title,
                content=payload.content,
                published=payload.published,
                author_id=payload.author_id,
                created_by=user.id,
            ),
        )

        return CreatePostResponseSchema(
            id=post_id,
        )
    except DomainError as e:
        Logger.warning(e)
        raise HTTPException(**e.to_http_args()) from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
