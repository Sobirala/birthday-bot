from typing import List

from sqlalchemy import BigInteger, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.enums import Language
from bot.models.base import Base, TimestampMixin
from bot.models.user import User


class Group(TimestampMixin, Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str]
    language: Mapped[Language] = mapped_column(default=Language.UA)
    collect: Mapped[bool] = mapped_column(default=False)
    users: Mapped[List["User"]] = relationship(
        secondary="usergrouplink",
        back_populates="groups",
        order_by=[func.date_part("month", User.birthday), func.extract("day", User.birthday)]
    )
