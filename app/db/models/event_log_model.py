from typing import Any

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Enum

from app.consts import EventLogType
from app.db.base import Base
from app.db.models.abstract_model import AbstractModel


class EventLog(Base, AbstractModel):

    __tablename__ = "event_log"

    event_type: Mapped[EventLogType] = mapped_column(
        Enum(*EventLogType, name="event_log_type"),
        nullable=False,
    )
    details: Mapped[dict[str, Any]] = mapped_column(type_=JSONB, nullable=False)
