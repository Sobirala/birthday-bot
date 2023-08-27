from typing import Generic, TypeVar, Sequence, Optional, Type, Any

from pydantic import BaseModel
from sqlalchemy import select, update, delete, func, ColumnElement, Select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from bot.models import Base


class BaseFilter(BaseModel):
    id: Optional[int] = None


Model = TypeVar('Model', bound=Base)
Filter = TypeVar('Filter', bound=BaseFilter)


class BaseRepository(Generic[Model, Filter]):
    __model__: Type[Model]

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_count(self) -> Optional[int]:
        query = select(func.count()).select_from(self.__model__)
        return await self._session.scalar(query)

    async def create(self, model: Model) -> Model:
        self._session.add(model)
        return model

    async def get(
            self,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            options: Optional[Sequence[ExecutableOption]] = None,
            order: Optional[Sequence[ColumnElement]] = None
    ) -> Sequence[Model]:
        query = select(self.__model__)

        query = self._set_filter(query, None, limit, offset, options, order)

        return (await self._session.scalars(query)).all()

    async def update(self, model_filter: Filter, **kwargs: Any) -> Optional[Model]:
        query = (update(self.__model__)
                 .values(**kwargs)
                 .execution_options(synchronize_session="evaluate")
                 .returning(self.__model__))

        query = self._set_filter(query, model_filter)

        return (await self._session.execute(query)).scalar()

    async def delete(self, model_filter: Filter) -> None:
        query = delete(self.__model__)

        query = self._set_filter(query, model_filter)

        await self._session.execute(query)

    async def find(
            self,
            model_filter: Filter,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            options: Optional[Sequence[ExecutableOption]] = None,
            order: Optional[Sequence[ColumnElement]] = None
    ) -> Sequence[Model]:
        query = select(self.__model__)

        query = self._set_filter(query, model_filter, limit, offset, options, order)

        return (await self._session.scalars(query)).all()

    async def find_one(
            self,
            model_filter: Filter,
            offset: Optional[int] = None,
            options: Optional[Sequence[ExecutableOption]] = None,
            order: Optional[Sequence[ColumnElement]] = None
    ) -> Optional[Model]:
        query = select(self.__model__).limit(1)

        query = self._set_filter(query, model_filter, 1, offset, options, order)

        return (await self._session.scalars(query)).first()

    @staticmethod
    def _set_filter(
            query: Select,
            model_filter: Optional[Filter] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            options: Optional[Sequence[ExecutableOption]] = None,
            order: Optional[Sequence[ColumnElement]] = None
    ) -> Select:
        if model_filter is not None:
            query = query.filter_by(**model_filter.model_dump(exclude_none=True))
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        if options is not None:
            query = query.options(*options)
        if order is not None:
            query = query.order_by(*order)
        return query

    async def check_exists(self, model_filter: Filter) -> bool:
        query = exists(self.__model__.id).select()

        query = self._set_filter(query, model_filter, 1)

        return await self._session.scalar(query)
