import asyncio
import logging

import motor.motor_asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis import asyncio as aioredis

from config import TGBotConfig
from handlers import inGroup, inPrivate, exceptions
from middlewares import ConfigVariables
from sheduler import Sheduler

logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG)


async def main():
    config = TGBotConfig()
    storage = RedisStorage(aioredis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        username=config.REDIS_USERNAME,
        password=config.REDIS_PASSWORD,
        db=config.REDIS_DB,
        decode_responses=True
    ))
    bot = Bot(token=config.TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=storage)
    client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGO_URL)
    db = client.birthdays

    scheduler = Sheduler(bot, db)
    await scheduler.start()

    dp.message.middleware(ConfigVariables(db))
    dp.callback_query.middleware(ConfigVariables(db))

    dp.include_router(inPrivate.router)
    dp.include_router(inGroup.router)
    dp.include_router(exceptions.router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
