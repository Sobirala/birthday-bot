from sqlalchemy.orm import Mapped, mapped_column

from bot.models.base import Base, TimestampMixin
from bot.types import Language


class Congratulation(TimestampMixin, Base):
    __tablename__ = "congratulations"

    photo_file_id: Mapped[str]
    language: Mapped[Language] = mapped_column(default=Language.UA)
    message: Mapped[str]
