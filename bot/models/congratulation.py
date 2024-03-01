from sqlalchemy.orm import Mapped, mapped_column

from bot.enums import Language
from bot.models.base import Base, TimestampMixin


class Congratulation(TimestampMixin, Base):
    __tablename__ = "congratulations"

    photo_file_id: Mapped[str]
    language: Mapped[Language] = mapped_column(default=Language.UK)
    message: Mapped[str]
