from typing import Generic, TypeVar, Sequence, Optional, Type, Any

from pydantic import BaseModel
from sqlalchemy import select, update, delete, func, ColumnElement, Select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from bot.models import Base

K = TypeVar('K', bound=Base)
V = TypeVar('V', bound=BaseModel)

class BaseRepository(Generic[K, V]):
    __model__: Type[K]

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_count(self) -> Optional[int]:
        query = select(func.count()).select_from(self.__model__)
        return await self._session.scalar(query)

    async def create(self, model: K) -> K:
        self._session.add(model)
        return model

    async def get(
            self,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            options: Optional[Sequence[ExecutableOption]] = None,
            order: Optional[Sequence[ColumnElement]] = None
    ) -> Sequence[K]:
        query = select(self.__model__)

        query = self._set_filter(query, None, limit, offset, options, order)

        return (await self._session.scalars(query)).all()

    async def get_by_id(
            self,
            model_id: int,
            options: Optional[Sequence[ExecutableOption]] = None
    ) -> Optional[K]:
        return await self._session.get(self.__model__, model_id, options=options)

    async def update(self, model_id: int, **kwargs: Any) -> None:
        query = update(self.__model__) \
            .where(self.__model__.id == model_id) \
            .values(**kwargs) \
            .execution_options(synchronize_session="evaluate")
        await self._session.execute(query)

    async def delete(self, model_id: int) -> None:
        query = delete(self.__model__).where(self.__model__.id == model_id)
        await self._session.execute(query)

    async def find(
            self,
            model_filter: V,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            options: Optional[Sequence[ExecutableOption]] = None,
            order: Optional[Sequence[ColumnElement]] = None
    ) -> Sequence[K]:
        query = select(self.__model__)

        query = self._set_filter(query, model_filter, limit, offset, options, order)

        return (await self._session.scalars(query)).all()

    async def find_one(
            self,
            model_filter: V,
            offset: Optional[int] = None,
            options: Optional[Sequence[ExecutableOption]] = None,
            order: Optional[Sequence[ColumnElement]] = None
    ) -> Optional[K]:
        query = select(self.__model__).limit(1)

        query = self._set_filter(query, model_filter, 1, offset, options, order)

        return (await self._session.scalars(query)).first()

    @staticmethod
    def _set_filter(
            query: Select,
            model_filter: Optional[V] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            options: Optional[Sequence[ExecutableOption]] = None,
            order: Optional[Sequence[ColumnElement]] = None
    ) -> Select:
        if model_filter is not None:
            query = query.filter_by(**model_filter.dict(exclude_none=True))
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        if options is not None:
            query = query.options(*options)
        if order is not None:
            query = query.order_by(*order)
        return query

    async def check_exists(self, model_filter: BaseModel) -> bool:
        query = exists(self.__model__.id).select()

        query = self._set_filter(query, model_filter, 1)

        return await self._session.scalar(query)
