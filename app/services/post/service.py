from pydantic import ValidationError

from app.db.dao.post_dao import DAOPostCreateDTO, PostDAO
from app.errors import CreatePostError, DomainError
from app.services.post.dto import PostCreateDTO
from app.services.post.schema import CreatePostValidation


class PostService:
    def __init__(self, *, post_dao: PostDAO) -> None:
        self.post_dao = post_dao

    async def create_post(
        self,
        *,
        data: "PostCreateDTO",
    ) -> int:

        try:
            validated_data = CreatePostValidation.model_validate(data)
        except ValidationError as e:
            raise DomainError(
                detail={
                    "code": CreatePostError.INVALID_DATA,
                    "message": "Post data validation failed.",
                },
            ) from e

        if validated_data.author_id % 2 == 1:
            raise DomainError(
                detail={
                    "code": CreatePostError.INVALID_AUTHOR_ID,
                    "message": "Author ID must be even.",
                },
            )

        post_id = await self.post_dao.create(
            DAOPostCreateDTO(
                title=validated_data.title,
                content=validated_data.content,
                published=validated_data.published,
                author_id=validated_data.author_id,
                created_by=validated_data.created_by,
            ),
        )

        return post_id
