from typing import Optional

from pydantic import BaseModel
from sqlalchemy import select, func

from bot.models import Congratulation
from bot.repositories.base import BaseRepository


class CongratulationFilter(BaseModel):
    photo_file_id: Optional[str] = None
    message: Optional[str] = None


class CongratulationRepository(BaseRepository[Congratulation, CongratulationFilter]):
    __model__ = Congratulation

    async def random(self) -> Optional[Congratulation]:
        query = select(self.__model__).order_by(func.random()).limit(1)

        return (await self._session.scalars(query)).first()
