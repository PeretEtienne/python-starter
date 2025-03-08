from dataclasses import dataclass
from typing import Optional


@dataclass
class PostUpdateDTO():
    title: Optional[str] = None
    content: Optional[str] = None


@dataclass
class PostCreateDTO():
    title: str
    content: str
    user_id: int
    published: bool = False
