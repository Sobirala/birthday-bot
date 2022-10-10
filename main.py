import logging

import motor.motor_asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.deep_linking import get_start_link, decode_payload

from config import *
from messages import *

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.birthdays

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)

@dp.message_handler(content_types=[types.ContentType.NEW_CHAT_MEMBERS]) #, types.ContentType.LEFT_CHAT_MEMBER
async def check_channel(message: types.Message):
    bot_id = (await bot.get_me())["id"]
    if message["new_chat_participant"]["id"] == bot_id:
        await message.answer(FIRST_ADD, parse_mode="HTML")
    else:
        await message.answer(ADD_MEMBER.format(username = message['new_chat_participant']['first_name'], id = message['new_chat_participant']['id']), parse_mode="HTML")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)