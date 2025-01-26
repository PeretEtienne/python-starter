from typing import AsyncGenerator
from fastapi import Request
from prisma import Prisma


async def get_db_session(request: Request) -> AsyncGenerator[Prisma]:
    """
    Create and get database session.

    :param request: current request.
    :yield: database session.
    """
    prisma = Prisma()
    await prisma.connect()

    try:
        yield prisma
    finally:
        await prisma.disconnect()
