from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import String

from app.db.base import Base
from app.db.models.abstract_model import AbstractModel


class Post(Base, AbstractModel):

    __tablename__ = "post"

    title: Mapped[str] = mapped_column(String(length=255), nullable=False)
    content: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    published: Mapped[bool] = mapped_column(default=False, nullable=False)
    author_id = mapped_column(
        Integer(),
        ForeignKey("user.id"),
        nullable=False,
        index=True,
    )
    author = relationship("User", foreign_keys=[author_id], lazy="selectin")
