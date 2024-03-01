from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.redis import (
    DefaultKeyBuilder,
    RedisEventIsolation,
    RedisStorage,
)
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram_dialog import setup_dialogs
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentCompileCore
from aiohttp import web
from redis.asyncio import Redis
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from bot.commands import set_bot_commands
from bot.enums import Language
from bot.middlewares.database import SessionMaker
from bot.middlewares.throttling import ThrottlingMiddleware
from bot.routers import router
from bot.services.scheduler import Scheduler
from bot.settings import settings
from bot.utils.logger import setup_logger
from bot.utils.redis_manager import RedisManager

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

redis: "Redis[Any]" = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    username=settings.REDIS_USERNAME,
    password=settings.REDIS_PASSWORD.get_secret_value(),
    decode_responses=True
)

core = FluentCompileCore(path="locales/{locale}/LC_MESSAGES")
manager = RedisManager(redis, Language.UK)


async def on_startup(bot: Bot) -> None:
    scheduler = Scheduler(bot, async_session, core, manager)
    scheduler.start()
    await bot.delete_webhook()
    await set_bot_commands(bot)
    if settings.USE_WEBHOOK:
        await bot.set_webhook(f"{settings.BASE_WEBHOOK_URL}{settings.WEBHOOK_PATH}", secret_token=settings.WEBHOOK_SECRET)


async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook()


def main() -> None:
    setup_logger()

    key_builder = DefaultKeyBuilder(with_destiny=True)
    storage = RedisStorage(redis, key_builder)
    events_isolation = RedisEventIsolation(redis, key_builder)
    bot = Bot(
        token=settings.TOKEN.get_secret_value(),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )
    dp = Dispatcher(
        storage=storage,
        events_isolation=events_isolation
    )

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    setup_dialogs(dp)

    i18n_middleware = I18nMiddleware(
        core=core,
        manager=manager,
        locale_key="locale",
        default_locale=Language.UK
    )
    i18n_middleware.setup(dp)

    dp.update.middleware(SessionMaker(sessionmaker=async_session))
    dp.update.middleware(ThrottlingMiddleware())

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
