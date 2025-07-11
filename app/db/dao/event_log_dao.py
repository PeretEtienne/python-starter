from dataclasses import dataclass
from typing import Any, Protocol

from app.consts import EventLogType
from app.db.dao.abstract_dao import AbstractDAO, DAOProtocol
from app.db.models.event_log_model import EventLog


class EventLogDAOProtocol(DAOProtocol[EventLog, "EventLogCreate", "EventLogUpdate"], Protocol):
    ...

class EventLogDAO(AbstractDAO[EventLog, "EventLogCreate", "EventLogUpdate"]):
    model = EventLog

@dataclass
class EventLogCreate:
    event_type: EventLogType
    details: dict[str, Any]
    created_by: int


@dataclass
class EventLogUpdate:
    updated_by: int
