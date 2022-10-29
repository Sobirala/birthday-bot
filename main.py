import asyncio
import logging

import motor.motor_asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis import asyncio as aioredis

from config import TGBotConfig
from handlers import inGroup, inPrivate
from middlewares import ConfigVariables

logging.basicConfig(level=logging.INFO)

async def main():
    config = TGBotConfig()
    storage = RedisStorage(aioredis.Redis(
        host = config.REDIS_HOST,
        port = config.REDIS_PORT,
        username = config.REDIS_USERNAME,
        password = config.REDIS_PASSWORD,
        db = 0,
        decode_responses=True
    ))
    bot = Bot(token=config.TOKEN)
    dp = Dispatcher(storage=storage)
    client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGO_URL)
    db = client.birthdays
    dp.message.middleware(ConfigVariables(db))
    dp.callback_query.middleware(ConfigVariables(db))

    dp.include_router(inPrivate.router)
    dp.include_router(inGroup.router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())