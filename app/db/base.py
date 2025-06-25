from sqlalchemy.orm import DeclarativeBase

from app.db.meta import meta


class Base(DeclarativeBase):

    metadata = meta
