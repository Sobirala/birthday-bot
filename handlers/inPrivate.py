from typing import Any
from aiogram import Bot, types, Router, F
from aiogram.filters import Command, CommandObject
from aiogram.utils.deep_linking import decode_payload
from aiogram.fsm.context import FSMContext

from messages.inPrivate import *
from states import *

router = Router()

@router.message(Command(commands=["start"]), F.chat.type.in_({"private"}))
async def start(message: types.Message, bot: Bot, database: Any, state: FSMContext, command: CommandObject):
    if command.args:
        await state.set_state(Form.year)
        chat = await bot.get_chat(decode_payload(command.args))
        await message.answer(ADD.format(groupname = chat.title), parse_mode="HTML")
        await message.answer(YEAR)
        return

@router.message(Command(commands=["help"]))
async def help(message: types.Message):
    return await message.reply(HELP)

@router.message(Form.year)
async def get_year(message: types.Message, state: FSMContext):
    await state.update_data(year=message.text)
    await state.set_state(Form.month)