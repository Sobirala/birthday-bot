import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from loguru import logger
from redis import asyncio as aioredis
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bot.services.google_maps import GoogleMaps
from bot.commands import set_bot_commands
from bot.config import Settings
from bot.handlers.group import router as group_router
from bot.handlers.private import router as private_router
from bot.keyboards.calendar_widget import Calendar
from bot.middlewares.database import SessionMaker
from bot.middlewares.i18n import TranslatorRunnerMiddleware
from bot.translator.hub import Translator
from bot.utils import logs


async def main():
    config = Settings()
    logs.setup(level=config.LOGLEVEL)
    engine = create_async_engine(
        URL.create(
            "postgresql+asyncpg",
            username=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD.get_secret_value(),
            host=config.POSTGRES_HOST,
            port=config.POSTGRES_PORT,
            database=config.POSTGRES_DB,
        )
    )
    async_session = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

    redis = aioredis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        username=config.REDIS_USERNAME,
        password=config.REDIS_PASSWORD.get_secret_value(),
        decode_responses=True
    )
    logger.debug(redis)
    storage = RedisStorage(redis=redis)
    bot = Bot(token=config.TOKEN.get_secret_value(), parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=storage)

    GoogleMaps(api_key=config.GOOGLE_TOKEN.get_secret_value())

    await Calendar.register_widget(dp)
    translator = Translator()

    dp.update.middleware(SessionMaker(sessionmaker=async_session))
    dp.update.middleware(TranslatorRunnerMiddleware(translator=translator))

    dp.include_router(private_router)
    dp.include_router(group_router)

    await set_bot_commands(bot)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
