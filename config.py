from os import environ
from typing import Final

class TGBotConfig():
    try:
        TOKEN: Final = environ["BOT_TOKEN"]
        MONGO_URL: Final = environ["MONGO_URL"]
        REDIS_HOST: Final = environ["REDIS_HOST"]
        REDIS_PORT: int = environ["REDIS_PORT"]
        REDIS_USERNAME: Final = environ["REDIS_USERNAME"]
        REDIS_PASSWORD: Final = environ["REDIS_PASSWORD"]
        GOOGLE_TOKEN: Final = environ["GOOGLE_TOKEN"]
    except Exception as key:
        raise RuntimeError(f"{key} must be defined!")

async def get_config_variable(varname):
    config = TGBotConfig()
    return getattr(config, varname)