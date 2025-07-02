# POST /posts
from pydantic import BaseModel


class CreatePostPayloadSchema(BaseModel):
    title: str
    content: str
    published: bool
    author_id: int


class CreatePostResponseSchema(BaseModel):
    id: int
