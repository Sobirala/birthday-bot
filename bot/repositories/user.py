import datetime
from typing import Optional, Sequence

from sqlalchemy import select, and_, ColumnElement, func, Interval
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.base import ExecutableOption
from sqlalchemy.sql.functions import concat

from bot.models import User, Group
from bot.repositories.base import BaseRepository, BaseFilter
from bot.enums import Gender


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

    async def get_birthday_persons(self, interval: int = 0) -> Sequence[User]:
        query = select(User).options(selectinload(User.groups)).filter(self._get_filter(interval))

        return (await self._session.scalars(query)).all()

    @staticmethod
    def _get_filter(interval: int = 0) -> ColumnElement[bool]:
        date = func.current_date()
        if interval != 0:
            date += func.cast(concat(interval, ' DAYS'), Interval)
        return and_(
            func.extract("MONTH", User.birthday) == func.extract("MONTH", date),
            func.extract("DAY", User.birthday) == func.extract("DAY", date),
            func.extract("HOUR", func.timezone(User.timezone, func.current_time())) == 9
        )

    async def get_birthday_group_users(self, birthday_id: int, group_id: int) -> Sequence[User]:
        query = select(User) \
                .select_from(Group) \
                .join(Group.users) \
                .filter(Group.id == group_id) \
                .filter(User.id != birthday_id)

        return (await self._session.scalars(query)).all()
