from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Integer

from app.db.models.timestamp_mixin import TimestampMixin


class AbstractModel(TimestampMixin, object):

    id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
        default=True,
    )
    created_by: Mapped[int] = mapped_column(
        Integer(),
        ForeignKey("user.id"),
        nullable=True,
    )
    updated_by: Mapped[int] = mapped_column(
        Integer(),
        ForeignKey("user.id"),
        nullable=True,
    )
