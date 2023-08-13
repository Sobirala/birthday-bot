from sqlalchemy.orm import Mapped

from bot.models.base import Base, TimestampMixin


class Congratulation(TimestampMixin, Base):
    __tablename__ = "congratulations"

    photo_file_id: Mapped[str]
    message: Mapped[str]
