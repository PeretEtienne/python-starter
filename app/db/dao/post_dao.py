from dataclasses import dataclass

from app.db.dao.abstract_dao import AbstractDAO
from app.db.models.post_model import Post


class PostDAO(
    AbstractDAO[Post, "DAOPostCreateDTO", "DAOPostUpdateDTO | DAOPublishedUpdateDTO"],
):
    model = Post

    async def create(self, data: "DAOPostCreateDTO") -> int:
        return await super().create(data)

    async def update(
        self,
        *,
        key: int,
        updates: "DAOPostUpdateDTO | DAOPublishedUpdateDTO",
    ) -> None:
        return await super().update(key=key, updates=updates)


@dataclass
class DAOPostCreateDTO:
    title: str
    content: str
    published: bool
    author_id: int
    created_by: int


@dataclass
class DAOPublishedUpdateDTO:
    published: bool
    updated_by: int


@dataclass
class DAOPostUpdateDTO:
    title: str
    content: str
    published: bool
    updated_by: int
