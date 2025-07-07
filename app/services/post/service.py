from pydantic import ValidationError

from app.db.dao.post_dao import DAOPostCreateDTO, PostDAO
from app.db.dao.user_dao import UserDAO
from app.errors import DomainError
from app.services.post.dto import PostCreateDTO
from app.services.post.errors import CreatePostError
from app.services.post.schema import CreatePostValidation


class PostService:
    def __init__(self, *, post_dao: PostDAO, user_dao: UserDAO) -> None:
        self.post_dao = post_dao
        self.user_dao = user_dao

    async def create_post(
        self,
        *,
        data: "PostCreateDTO",
    ) -> int:

        try:
            validated_data = CreatePostValidation.model_validate(data)
        except ValidationError as e:
            errors = "; ".join(err["msg"] for err in e.errors())
            raise DomainError(
                detail={
                    "code": CreatePostError.INVALID_DATA,
                    "message": errors,
                },
            ) from e


        author = await self.user_dao.get_by_id(validated_data.author_id)

        if not author:
            raise DomainError(
                detail={
                    "code": CreatePostError.AUTHOR_NOT_FOUND,
                    "message": "Author not found.",
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
