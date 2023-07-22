from typing import Optional, Sequence

from pydantic import BaseModel
from sqlalchemy import select, ColumnElement
from sqlalchemy.sql.base import ExecutableOption

from bot.models import Group
from bot.repositories.base import BaseRepository


class GroupFilter(BaseModel):
    chat_id: Optional[int] = None
    title: Optional[str] = None
    collect: Optional[bool] = None


class GroupRepository(BaseRepository[Group, GroupFilter]):
    __model__ = Group
