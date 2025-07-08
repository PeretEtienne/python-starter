from dataclasses import dataclass


@dataclass
class PostCreatedEvent():
    id: int
    title: str
    published: bool
    author_id: int
