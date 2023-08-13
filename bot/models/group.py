from typing import TYPE_CHECKING, List

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.models.base import Base, TimestampMixin
from bot.types import Language

if TYPE_CHECKING:
    from .user import User


class Group(TimestampMixin, Base):
    __tablename__ = "groups"

    chat_id: Mapped[int] = mapped_column(BigInteger, index=True, unique=True)
    title: Mapped[str]
    language: Mapped[Language] = mapped_column(default=Language.UA)
    collect: Mapped[bool] = mapped_column(default=False)
    users: Mapped[List["User"]] = relationship(
        secondary="usergrouplink", back_populates="groups"
    )
