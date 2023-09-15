import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.enums import Gender, Language
from bot.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from bot.models.group import Group


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fullname: Mapped[str]
    gender: Mapped[Gender]
    language: Mapped[Language] = mapped_column(default=Language.UA)
    timezone: Mapped[str]
    birthday: Mapped[datetime.date]
    groups: Mapped[List["Group"]] = relationship(secondary="usergrouplink", back_populates="users")
