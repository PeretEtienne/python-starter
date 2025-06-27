import logging
from typing import Generic, Sequence, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.abstract_model import AbstractModel
from app.settings import settings

logger = logging.getLogger(settings.logger_name)

TModel = TypeVar("TModel", bound=AbstractModel)
TCreate = TypeVar("TCreate", bound=BaseModel)
TUpdate = TypeVar("TUpdate", bound=BaseModel)


class AbstractDAO(Generic[TModel, TCreate, TUpdate]):
    session: AsyncSession
    model: Type[TModel]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: TCreate) -> int:
        model = self.model(**data.model_dump())
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return model.id

    async def get_all(
        self,
        limit: int = 10,
        offset: int = 0,
    ) -> Sequence[TModel]:
        query = select(self.model).where(self.model.is_active.is_(True)).offset(offset)

        if limit > 0:
            query = query.limit(limit)

        raw_models = await self.session.execute(query)

        return raw_models.scalars().fetchall()

    async def get_by_id(self, key: int) -> TModel | None:
        if not hasattr(self.model, "id"):
            raise NotImplementedError("Model has no id field")

        query = select(self.model).where(
            self.model.id == key and self.model.is_active.is_(True),
        )

        rows = await self.session.execute(query)
        return rows.scalars().first()

    async def update(self, key: int, updates: TUpdate) -> None:
        if not hasattr(self.model, "id"):
            raise NotImplementedError("Model has no id field")

        query = select(self.model).where(self.model.id == key)
        row = await self.session.execute(query)
        model = row.scalars().first()

        if not model:
            raise ValueError("Model not found")

        if hasattr(model, "updated_by") and hasattr(updates, "updated_by"):
            logger.warning("Missing updated_by_id when updating model")

        for attr, value in updates.model_dump().items():
            setattr(model, attr, value)

        if hasattr(model, "updated_at"):
            model.updated_at = func.now()

        await self.session.flush()
        await self.session.refresh(model)

    async def delete(self, key: int) -> None:
        if not hasattr(self.model, "id"):
            raise NotImplementedError("Model has no id field")

        row = await self.session.execute(select(self.model).where(self.model.id == key))

        already_dead = row.scalars().first()

        if not already_dead:
            raise ValueError("Model not found")

        await self.session.delete(already_dead)

    async def archive(self, key: int, user_id: int) -> None:

        if not hasattr(self.model, "id"):
            raise NotImplementedError("Model has no id field")

        query = select(self.model).where(self.model.id == key)
        row = await self.session.execute(query)
        model = row.scalars().first()

        if not model:
            raise ValueError("Model not found")

        if not model.is_active:
            raise ValueError("Model is already archived")

        model.is_active = False
        model.updated_at = func.now()
        model.updated_by = user_id

        await self.session.flush()
        await self.session.refresh(model)

    async def restore(self, key: int, user_id: int) -> None:
        if not hasattr(self.model, "id"):
            raise NotImplementedError("Model has no id field")

        query = select(self.model).where(self.model.id == key)
        row = await self.session.execute(query)
        model = row.scalars().first()

        if not model:
            raise ValueError("Model not found")

        if model.is_active:
            raise ValueError("Model is already restored")

        model.is_active = True
        model.updated_at = func.now()
        model.updated_by = user_id

        await self.session.flush()
        await self.session.refresh(model)
