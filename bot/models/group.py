from enum import Enum
from typing import List, Optional

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.models.base import Base, TimestampMixin


class UserGroupLink(Base):
    __tablename__ = "usergrouplink"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), primary_key=True)


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"


class Language(Enum):
    EN = "en"
    UA = "ua"
    RU = "ru"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(index=True, unique=True)
    username: Mapped[Optional[str]] = mapped_column(String(32))
    fullname: Mapped[str] = mapped_column(String(129))
    gender: Mapped[Gender]
    language: Mapped[Language] = mapped_column(default=Language.UA)
    address: Mapped[str] = mapped_column(String(256))
    timezone: Mapped[str] = mapped_column(String(32))
    groups: Mapped[List["Group"]] = relationship(
        secondary="usergrouplink", back_populates="users"
    )


class Group(TimestampMixin, Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(index=True, unique=True)
    title: Mapped[str] = mapped_column(String(255))
    language: Mapped[Language] = mapped_column(default=Language.UA)
    collect: Mapped[bool] = mapped_column(default=False)
    users: Mapped[List["User"]] = relationship(
        secondary="usergrouplink", back_populates="groups"
    )
