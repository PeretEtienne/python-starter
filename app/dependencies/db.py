from typing import Any, AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.db.models.user_model import User


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = request.app.state.db_session_factory()

    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_user_db(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[Any, Any]:
    yield SQLAlchemyUserDatabase(session, User)
