from typing import Any

from pydantic import BaseModel, ConfigDict

from app.consts import EventLogType
from app.db.dao.abstract_dao import AbstractDAO
from app.db.models.event_log_model import EventLog


class EventLogCreate(BaseModel):
    event_type: EventLogType
    details: dict[str, Any]
    created_by: int

    model_config = ConfigDict(
        extra="ignore",
    )


class EventLogUpdate(BaseModel):

    model_config = ConfigDict(
        extra="ignore",
    )


class EventLogDAO(AbstractDAO[EventLog, EventLogCreate, EventLogUpdate]):
    model = EventLog
