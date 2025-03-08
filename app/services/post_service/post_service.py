
from prisma.models import Post, User
from prisma.partials import PostWithAuthor
from prisma.types import PostCreateInput, PostUpdateInput

from app.repository.post_repository.post_repository import PostRepository
from app.repository.user_repository.user_repository import UserRepository
from app.services.post_service.dto import PostCreateDTO, PostUpdateDTO
from app.services.post_service.errors import NotAuthorizedPatchPostError, PostNotFoundError


class PostService():
    def __init__(
        self,
        post_repo: PostRepository,
        user_repo: UserRepository,
    ) -> None:
        self.post_repo = post_repo
        self.user_repo = user_repo

    async def create_post(
        self,
        user_id: int,
        dto: PostCreateDTO,
    ) -> None:
        post_create_input = PostCreateInput(
            title=dto.title,
            content=dto.content,
            published=dto.published,
            author_id=user_id,
        )

        await self.post_repo.create(post_create_input)

    async def get_post(self, post_id: int) -> Post:
        post = await self.post_repo.get_by_id(post_id)

        if not post:
            raise PostNotFoundError("Post not found")

        return post

    async def get_published(self) -> list[PostWithAuthor]:
        return await self.post_repo.get_published()

    async def patch_post(
        self,
        user: User,
        post_id: int,
        updates_dto: PostUpdateDTO,
    ) -> None:
        post = await self.post_repo.get_by_id(post_id)

        if not post:
            raise PostNotFoundError("Post not found")

        if post.author_id != user.id:
            raise NotAuthorizedPatchPostError("You are not the author of this post")

        post_update_input = PostUpdateInput()

        if (updates_dto.title):
            post_update_input["title"] = updates_dto.title

        if (updates_dto.content):
            post_update_input["content"] = updates_dto.content

        await self.post_repo.patch_post(post_id, post_update_input)
