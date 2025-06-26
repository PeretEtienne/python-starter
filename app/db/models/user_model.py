from datetime import datetime
from typing import Optional

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import DateTime, String

from app.consts import Permission
from app.db.base import Base
from app.db.models.abstract_model import AbstractModel
from app.db.models.timestamp_mixin import TimestampMixin


class User(Base, SQLAlchemyBaseUserTable[int], AbstractModel, TimestampMixin):

    first_name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    permissions: Mapped[list[Permission]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=[],
    )
    refresh_token: Mapped[str] = mapped_column(String(length=1024), nullable=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime())
