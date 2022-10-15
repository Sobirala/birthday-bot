import asyncio
from distutils.command.config import config
import logging

import motor.motor_asyncio
from aiogram import Bot, Dispatcher

from config import TGBotConfig
from handlers import inGroup, inPrivate
from middlewares import GetDBVariable

logging.basicConfig(level=logging.INFO)

async def main():
    config = TGBotConfig()
    bot = Bot(token=config.TOKEN)
    dp = Dispatcher()
    client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGO_URL)
    db = client.birthdays
    dp.message.middleware(GetDBVariable(db))

    dp.include_router(inPrivate.router)
    dp.include_router(inGroup.router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())