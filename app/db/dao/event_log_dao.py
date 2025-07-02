from dataclasses import dataclass
from typing import Any

from app.consts import EventLogType
from app.db.dao.abstract_dao import AbstractDAO
from app.db.models.event_log_model import EventLog


@dataclass
class EventLogCreate:
    event_type: EventLogType
    details: dict[str, Any]
    created_by: int


@dataclass
class EventLogUpdate:
    updated_by: int


class EventLogDAO(AbstractDAO[EventLog, EventLogCreate, EventLogUpdate]):
    model = EventLog
