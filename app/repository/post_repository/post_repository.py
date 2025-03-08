from prisma import Prisma
from prisma.models import Post
from prisma.partials import PostWithAuthor
from prisma.types import PostCreateInput, PostUpdateInput


class PostRepository():
    def __init__(self, db: Prisma) -> None:
        self.db = db

    async def create(self, data: PostCreateInput) -> Post:
        return await self.db.post.create(data=data)

    async def get_by_id(self, post_id: int) -> Post | None:
        return await self.db.post.find_unique(where={
            "id": post_id,
        })

    async def get_published(self) -> list[PostWithAuthor]:
        return await PostWithAuthor.prisma().find_many(
            where={
                "published": True,
                "author": {
                    "is": {
                        "first_name": {
                            "contains": "test",
                        },
                    },
                },
            },
            include={
                "author": True,
            },
        )

    async def patch_post(self, post_id: int, updates: PostUpdateInput) -> Post | None:
        return await self.db.post.update(
            data=updates,
            where={
                "id": post_id,
            },
        )
