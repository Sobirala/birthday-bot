import datetime
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.sql.base import ExecutableOption

from bot.models import User, Group
from bot.repositories.base import BaseRepository, BaseFilter
from bot.types import Gender


class UserFilter(BaseFilter):
    user_id: Optional[int] = None
    fullname: Optional[str] = None
    gender: Optional[Gender] = None
    timezone: Optional[str] = None
    birthday: Optional[datetime.date] = None


class UserRepository(BaseRepository[User, UserFilter]):
    __model__ = User

    async def get_user_in_group(self, user_id: int, chat_id: int, options: Optional[Sequence[ExecutableOption]] = None) -> Optional[User]:
        query = select(User) \
            .join(User.groups) \
            .filter(Group.chat_id == chat_id) \
            .filter(User.user_id == user_id) \
            .limit(1)

        if options is not None:
            query = query.options(*options)

        return (await self._session.scalars(query)).first()
