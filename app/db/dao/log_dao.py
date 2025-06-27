from typing import Any

from pydantic import BaseModel

from app.consts import LogEventType
from app.db.dao.abstract_dao import AbstractDAO
from app.db.models.log_model import Log


class LogEventCreate(BaseModel):
    event_type: LogEventType
    details: dict[str, Any]
    created_by: int

class LogEventUpdate(BaseModel):
    pass

class LogEventDAO(AbstractDAO[Log, LogEventCreate, LogEventUpdate]):
    model = Log
