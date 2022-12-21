from aiogram import types, Router
from aiogram.filters import Command

from bot.messages.inPrivate import *

router = Router()


@router.message(Command(commands=["help"]))
async def help_commands(message: types.Message):
    return await message.answer(HELP)
