import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
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


async def on_startup(bot: Bot):
    await bot.delete_webhook()
    await set_bot_commands(bot)
    if settings.USE_WEBHOOK:
        await bot.set_webhook(f"{settings.BASE_WEBHOOK_URL}{settings.WEBHOOK_PATH}", secret_token=settings.WEBHOOK_SECRET)


def main():
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

    dp.startup.register(on_startup)

    scheduler = Scheduler(bot, async_session)
    scheduler.start()

    Calendar.register_widget(dp)
    translator = Translator()

    dp.update.middleware(SessionMaker(sessionmaker=async_session))
    dp.update.middleware(TranslatorRunnerMiddleware(translator=translator))

    dp.include_router(router)

    if settings.USE_WEBHOOK:
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=settings.WEBHOOK_SECRET
        )
        webhook_requests_handler.register(app, path=settings.WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        web.run_app(app, host=settings.WEB_SERVER_HOST, port=settings.WEB_SERVER_PORT)
    else:
        dp.run_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    main()
