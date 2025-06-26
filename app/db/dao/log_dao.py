from typing import Any

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.consts import LogEvent
from app.db.dao.abstract_dao import AbstractDAO
from app.db.models.log_model import Log
from app.dependencies.db import get_db_session


class LogCreate(BaseModel):
    event: LogEvent
    details: dict[str, Any]
    created_by: int

class LogUpdate(BaseModel):
    pass

class LogDAO(AbstractDAO[Log, LogCreate, LogUpdate]):
    model = Log

    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session
