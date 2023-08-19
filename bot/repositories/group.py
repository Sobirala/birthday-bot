from typing import Optional

from bot.models import Group
from bot.repositories.base import BaseRepository, BaseFilter


class GroupFilter(BaseFilter):
    chat_id: Optional[int] = None
    title: Optional[str] = None
    collect: Optional[bool] = None


class GroupRepository(BaseRepository[Group, GroupFilter]):
    __model__ = Group
