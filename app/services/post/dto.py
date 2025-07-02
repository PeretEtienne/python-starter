from dataclasses import dataclass


@dataclass
class PostCreateDTO:
    title: str
    content: str
    published: bool
    author_id: int
    created_by: int
