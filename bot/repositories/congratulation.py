from typing import Optional

from sqlalchemy import func, select

from bot.enums import Language
from bot.models import Congratulation
from bot.repositories.base import BaseFilter, BaseRepository


class CongratulationFilter(BaseFilter):
    photo_file_id: Optional[str] = None
    language: Optional[Language] = None
    message: Optional[str] = None


class CongratulationRepository(BaseRepository[Congratulation, CongratulationFilter]):
    __model__ = Congratulation

    async def random(self, model_filter: CongratulationFilter) -> Optional[Congratulation]:
        query = select(self.__model__).order_by(func.random())

        query = self._set_filter_with_additions(query, model_filter, 1)

        return (await self._session.scalars(query)).first()