from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import AsyncIterator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class SessionManager:
    def __init__(self) -> None:
        self._factory: Optional[async_sessionmaker[AsyncSession]] = None

    def init(self, factory: async_sessionmaker[AsyncSession]) -> None:
        self._factory = factory

    def ensure_initialized(self) -> async_sessionmaker[AsyncSession]:
        if not self._factory:
            raise RuntimeError("Session factory has not been initialized")
        return self._factory

    def context(self) -> AbstractAsyncContextManager[AsyncSession]:
        return session_context(self.ensure_initialized())

@asynccontextmanager
async def session_context(factory: async_sessionmaker[AsyncSession]) -> AsyncIterator[AsyncSession]:
    session = factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


session_manager = SessionManager()
