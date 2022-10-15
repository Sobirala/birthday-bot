from os import environ
from typing import Final

class TGBotConfig():
    TOKEN: Final = environ.get("BOT_TOKEN", default=lambda: RuntimeError("Telegram token must be defined!"))
    MONGO_URL: Final = environ.get("MONGO_URL", default=lambda: RuntimeError("Telegram token must be defined!"))