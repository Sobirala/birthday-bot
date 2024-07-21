from typing import Any, Generic, Optional, Sequence, Tuple, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import (
    ColumnElement,
    Select,
    delete,
    exists,
    func,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption
from sqlalchemy.sql.dml import DMLWhereBase

from bot.models import Base


class BaseFilter(BaseModel):
    id: Optional[int] = None


Model = TypeVar('Model', bound=Base)
Filter = TypeVar('Filter', bound=BaseFilter)

Query = Union[Select[Any], DMLWhereBase]


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

    async def merge(self, model: Model) -> Model:
        await self._session.merge(model)
        return model

    async def get(
            self,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            options: Optional[Sequence[ExecutableOption]] = None,
            order: Optional[Sequence[ColumnElement[Model]]] = None
    ) -> Sequence[Model]:
        query = select(self.__model__)

        query = self._set_filter_with_additions(query, None, limit, offset, options, order)

        return (await self._session.scalars(query)).all()

    async def update(self, model_filter: Filter, **kwargs: Any) -> Sequence[Model]:
        query = (update(self.__model__)
                 .values(**kwargs)
                 .execution_options(synchronize_session="evaluate")
                 .returning(self.__model__))

        query = self._set_filter(query, model_filter)  # type: ignore[assignment]

        return (await self._session.scalars(query)).all()

    async def delete(self, model_filter: Filter) -> None:
        query = delete(self.__model__)

        query = self._set_filter(query, model_filter)  # type: ignore[assignment]

        await self._session.execute(query)

    async def find(
            self,
            model_filter: Filter,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            options: Optional[Sequence[ExecutableOption]] = None,
            order: Optional[Sequence[ColumnElement[Model]]] = None
    ) -> Sequence[Model]:
        query = select(self.__model__)

        query = self._set_filter_with_additions(query, model_filter, limit, offset, options, order)

        return (await self._session.scalars(query)).all()

    async def find_one(
            self,
            model_filter: Filter,
            offset: Optional[int] = None,
            options: Optional[Sequence[ExecutableOption]] = None,
            order: Optional[Sequence[ColumnElement[Model]]] = None
    ) -> Optional[Model]:
        query = select(self.__model__).limit(1)

        query = self._set_filter_with_additions(query, model_filter, 1, offset, options, order)

        return (await self._session.scalars(query)).first()

    @staticmethod
    def _set_filter(
            query: Union[Select[Tuple[Model]], DMLWhereBase],
            model_filter: Optional[Filter] = None
    ) -> Union[Select[Tuple[Model]], DMLWhereBase]:
        if model_filter is not None:
            query = query.filter_by(**model_filter.model_dump(exclude_none=True))
        return query

    @staticmethod
    def _set_additions(
            query: Select[Tuple[Model]],
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            options: Optional[Sequence[ExecutableOption]] = None,
            order: Optional[Sequence[ColumnElement[Model]]] = None
    ) -> Select[Tuple[Model]]:
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        if options is not None:
            query = query.options(*options)
        if order is not None:
            query = query.order_by(*order)
        return query

    def _set_filter_with_additions(
            self,
            query: Select[Tuple[Any]],
            model_filter: Optional[Filter] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            options: Optional[Sequence[ExecutableOption]] = None,
            order: Optional[Sequence[ColumnElement[Model]]] = None
    ) -> Select[Tuple[Any]]:
        query = self._set_filter(query, model_filter)  # type: ignore[assignment]
        query = self._set_additions(query, limit, offset, options, order)
        return query

    async def check_exists(self, model_filter: Filter) -> Optional[bool]:
        query = exists(self.__model__.id).select()

        query = self._set_filter_with_additions(query, model_filter, 1)

        return await self._session.scalar(query)
