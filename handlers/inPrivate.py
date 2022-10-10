from aiogram import types, Router
from messages import *
from aiogram.filters import Command

router = Router()

@router.message(Command(commands=["start"]))
async def cmd_send_welcome(message: types.Message):
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")