import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.models.base import Base, TimestampMixin
from bot.models.enums import Gender, Language

if TYPE_CHECKING:
    from bot.models.group import Group


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True, unique=True)
    username: Mapped[Optional[str]] = mapped_column(String(32))
    fullname: Mapped[str] = mapped_column(String(129))
    gender: Mapped[Gender]
    language: Mapped[Language] = mapped_column(default=Language.UA)
    address: Mapped[str] = mapped_column(String(256))
    timezone: Mapped[str] = mapped_column(String(32))
    birthday: Mapped[datetime.date]
    groups: Mapped[List["Group"]] = relationship(
        secondary="usergrouplink", back_populates="users"
    )
