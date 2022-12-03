import asyncio

import motor.motor_asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis import asyncio as aioredis

from config import Settings
from handlers import inGroup, inPrivate, exceptions
from middlewares import ConfigVariables
from scheduler import Scheduler
from utils import logs


async def main():
    config = Settings()

    logs.setup(level=config.LOGLEVEL)

    storage = RedisStorage(aioredis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        username=config.REDIS_USERNAME,
        password=config.REDIS_PASSWORD.get_secret_value(),
        db=config.REDIS_DB,
        decode_responses=True
    ))
    bot = Bot(token=config.TOKEN.get_secret_value(), parse_mode="HTML")
    dp = Dispatcher(storage=storage)
    client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGO_URL.get_secret_value())
    db = client.birthdays

    scheduler = Scheduler(bot, db)
    await scheduler.start()

    dp.message.middleware(ConfigVariables(db, config))
    dp.callback_query.middleware(ConfigVariables(db, config))

    dp.include_router(inPrivate.router)
    dp.include_router(inGroup.router)
    dp.include_router(exceptions.router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
