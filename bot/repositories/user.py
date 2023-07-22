import datetime
from typing import Optional

from pydantic import BaseModel

from bot.models import User
from bot.models.enums import Gender
from bot.repositories.base import BaseRepository


class UserFilter(BaseModel):
    user_id: Optional[int] = None
    fullname: Optional[str] = None
    gender: Optional[Gender] = None
    timezone: Optional[str] = None
    birthday: Optional[datetime.date] = None


class UserRepository(BaseRepository[User, UserFilter]):
    __model__ = User
