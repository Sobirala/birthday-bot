from typing import Optional

from bot.models import Group
from bot.repositories.base import BaseFilter, BaseRepository


class GroupFilter(BaseFilter):
    title: Optional[str] = None
    collect: Optional[bool] = None


class GroupRepository(BaseRepository[Group, GroupFilter]):
    __model__ = Group
