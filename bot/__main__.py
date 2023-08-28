import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis import asyncio as aioredis
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bot.commands import set_bot_commands
from bot.settings import settings
from bot.keyboards.calendar_widget import Calendar
from bot.middlewares.database import SessionMaker
from bot.middlewares.i18n import TranslatorRunnerMiddleware
from bot.routers import router
from bot.services.scheduler import Scheduler
from bot.translator.hub import Translator
from bot.utils.logger import setup_logger


async def main():
    setup_logger()
    engine = create_async_engine(
        URL.create(
            "postgresql+asyncpg",
            username=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD.get_secret_value(),
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB,
        )
    )
    async_session = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

    redis = aioredis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        username=settings.REDIS_USERNAME,
        password=settings.REDIS_PASSWORD.get_secret_value(),
        decode_responses=True
    )

    storage = RedisStorage(redis=redis)
    bot = Bot(token=settings.TOKEN.get_secret_value(), parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=storage)

    scheduler = Scheduler(bot, async_session)
    await scheduler.start()

    Calendar.register_widget(dp)
    translator = Translator()

    dp.update.middleware(SessionMaker(sessionmaker=async_session))
    dp.update.middleware(TranslatorRunnerMiddleware(translator=translator))

    dp.include_router(router)

    await dp.start_polling(bot)
    await set_bot_commands(bot)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
