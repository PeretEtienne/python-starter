from pydantic import BaseModel, Field


# POST /posts
class CreatePostPayloadSchema(BaseModel):
    title: str = Field(..., max_length=5)
    content: str
    published: bool = False


# POST /posts/:post_id
class PatchPostPayloadSchema(BaseModel):
    title: str = Field(..., max_length=5)
    content: str
