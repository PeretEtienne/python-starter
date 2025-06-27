from typing import Any

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Enum

from app.consts import LogEventType
from app.db.base import Base
from app.db.models.abstract_model import AbstractModel


class EventLog(Base, AbstractModel):

    __tablename__ = "event_log"

    event_type: Mapped[LogEventType] = mapped_column(
        Enum(*LogEventType, name="log_event_type"),
        nullable=False,
    )
    details: Mapped[dict[str, Any]] = mapped_column(type_=JSONB, nullable=False)
