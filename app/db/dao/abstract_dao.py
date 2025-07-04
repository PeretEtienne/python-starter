import logging
from dataclasses import Field as DCField
from dataclasses import asdict
from typing import Any, ClassVar, Generic, Protocol, Sequence, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.abstract_model import AbstractModel
from app.settings import settings

logger = logging.getLogger(settings.logger_name)


class DataclassInstanceCreate(Protocol):
    __dataclass_fields__: ClassVar[dict[str, DCField[Any]]]

    created_by: int


class DataclassInstanceUpdate(Protocol):
    __dataclass_fields__: ClassVar[dict[str, DCField[Any]]]

    updated_by: int


TModel = TypeVar("TModel", bound=AbstractModel)
TCreate = TypeVar("TCreate", bound=DataclassInstanceCreate)
TUpdate = TypeVar("TUpdate", bound=DataclassInstanceUpdate)


class AbstractDAO(Generic[TModel, TCreate, TUpdate]):
    session: AsyncSession
    model: Type[TModel]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: TCreate) -> int:
        model = self.model(**asdict(data))
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return model.id

    async def get_all(
        self,
        *,
        limit: int = 10,
        offset: int = 0,
    ) -> Sequence[TModel]:
        query = select(self.model).where(self.model.is_active.is_(True)).offset(offset)

        if limit > 0:
            query = query.limit(limit)

        raw_models = await self.session.execute(query)

        return raw_models.scalars().fetchall()

    async def get_by_id(self, key: int) -> TModel | None:
        query = select(self.model).where(
            self.model.id == key and self.model.is_active.is_(True),
        )

        rows = await self.session.execute(query)
        return rows.scalars().first()

    async def update(self, *, key: int, updates: TUpdate) -> None:
        query = select(self.model).where(self.model.id == key)
        row = await self.session.execute(query)
        model = row.scalars().first()

        if not model:
            raise ValueError("Model not found")

        for attr, value in asdict(updates).items():
            setattr(model, attr, value)

        model.updated_at = func.now()

        await self.session.flush()
        await self.session.refresh(model)

    async def delete(self, key: int) -> None:
        row = await self.session.execute(select(self.model).where(self.model.id == key))

        already_dead = row.scalars().first()

        if not already_dead:
            raise ValueError("Model not found")

        await self.session.delete(already_dead)

    async def archive(self, key: int, updated_by: int) -> None:

        query = select(self.model).where(self.model.id == key)
        row = await self.session.execute(query)
        model = row.scalars().first()

        if not model:
            raise ValueError("Model not found")

        if not model.is_active:
            raise ValueError("Model is already archived")

        model.is_active = False
        model.updated_at = func.now()
        model.updated_by = updated_by

        await self.session.flush()
        await self.session.refresh(model)

    async def restore(self, key: int, updated_by: int) -> None:
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
        model.updated_by = updated_by

        await self.session.flush()
        await self.session.refresh(model)
