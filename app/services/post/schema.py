from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_validator


class CreatePostValidation(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=500)
    published: bool
    author_id: PositiveInt
    created_by: PositiveInt

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        if value.startswith("DRAFT -"):
            raise ValueError("Title cannot start with 'DRAFT -'")

        return value

    @field_validator("author_id")
    @classmethod
    def validate_author_id(cls, value: int) -> int:
        if value % 2 != 0:
            raise ValueError("Author ID must be even")

        return value

    model_config = ConfigDict(from_attributes=True)
