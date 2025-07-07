from enum import StrEnum


class CreatePostError(StrEnum):
    INVALID_DATA = "INVALID_DATA"
    AUTHOR_NOT_FOUND = "AUTHOR_NOT_FOUND"
