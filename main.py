import asyncio
import logging

import motor.motor_asyncio
from aiogram import Bot, Dispatcher

from config import *
from handlers import inGroup, inPrivate

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client.birthdays

    dp.include_router(inPrivate.router)
    dp.include_router(inGroup.router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())