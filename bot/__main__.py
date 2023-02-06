import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis import asyncio as aioredis
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from bot.config import Settings
from bot.utils import logs


async def main():
    config = Settings()

    logs.setup(level=config.LOGLEVEL)

    engine = create_async_engine(URL.create(
            "postgresql+asyncpg",
            username=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD.get_secret_value(),
            host=config.POSTGRES_HOST,
            port=config.POSTGRES_PORT,
            database=config.POSTGRES_DB,
        ),
        echo=True
    )
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    redis = aioredis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        username=config.REDIS_USERNAME,
        password=config.REDIS_PASSWORD.get_secret_value(),
        decode_responses=True
    )
    storage = RedisStorage(redis=redis)
    bot = Bot(token=config.TOKEN.get_secret_value(), parse_mode="HTML")
    dp = Dispatcher(storage=storage)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
