from typing import AsyncGenerator

from prisma import Prisma


async def get_db_session(
        use_transaction: bool = False,
) -> AsyncGenerator[Prisma, None]:
    """
    Create and get database session.

    :param request: current request.
    :yield: database session.
    """
    prisma = Prisma()
    await prisma.connect()

    transaction = prisma.tx()
    result = await transaction.start() if use_transaction else prisma

    try:
        yield result
        if use_transaction:
            await transaction.commit()

    except Exception as e:
        if use_transaction:
            await transaction.rollback()
        raise e
    finally:
        await prisma.disconnect()
