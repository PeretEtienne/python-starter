from dataclasses import dataclass
from typing import Protocol

from app.db.dao.abstract_dao import AbstractDAO, DAOProtocol
from app.db.models.post_model import Post


class PostDAOProtocol(
    DAOProtocol[Post, "DAOPostCreateDTO", "DAOPostUpdateDTO | DAOPublishedUpdateDTO"],
    Protocol,
):
    ...

class PostDAO(
    AbstractDAO[Post, "DAOPostCreateDTO", "DAOPostUpdateDTO | DAOPublishedUpdateDTO"],
):
    model = Post

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
