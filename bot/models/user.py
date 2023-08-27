import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.models.base import Base, TimestampMixin
from bot.enums import Gender, Language

if TYPE_CHECKING:
    from bot.models.group import Group


class User(TimestampMixin, Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, index=True, unique=True)
    fullname: Mapped[str]
    gender: Mapped[Gender]
    language: Mapped[Language] = mapped_column(default=Language.UA)
    timezone: Mapped[str]
    birthday: Mapped[datetime.date]
    groups: Mapped[List["Group"]] = relationship(
        secondary="usergrouplink", back_populates="users"
    )

    def __repr__(self):
        return f"<User id={self.id} name={self.fullname}>"
