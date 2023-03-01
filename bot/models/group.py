from typing import TYPE_CHECKING, List

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.models.base import Base, TimestampMixin
from bot.models.enums import Language

if TYPE_CHECKING:
    from .user import User


class Group(TimestampMixin, Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True, unique=True)
    title: Mapped[str] = mapped_column(String(255))
    language: Mapped[Language] = mapped_column(default=Language.UA)
    collect: Mapped[bool] = mapped_column(default=False)
    users: Mapped[List["User"]] = relationship(
        secondary="usergrouplink", back_populates="groups"
    )
