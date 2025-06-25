from typing import Any

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Enum

from app.consts import LogEvent
from app.db.base import Base
from app.db.models.abstract_model import AbstractModel


class Log(Base, AbstractModel):

    event: Mapped[LogEvent] = mapped_column(
        Enum(*LogEvent, name="log_event"),
        nullable=False,
    )
    details: Mapped[dict[str, Any]] = mapped_column(type_=JSONB, nullable=False)
