from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column


class AbstractModel(object):

    id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),
        server_default=func.now(),
    )
