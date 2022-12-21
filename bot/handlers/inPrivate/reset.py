from aiogram import Bot, types, Router
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext

from bot.buttons import submit
from bot.messages.inPrivate import *
from bot.states import *

router = Router()


@router.message(Command(commands=["reset"]))
async def reset(message: types.Message):
    return await message.answer(RESET, reply_markup=submit)


@router.callback_query(Text("submit"))
async def submit_change(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    await state.set_state(Form.year)
    await state.update_data(update=True)
    await bot.send_message(callback.from_user.id, YEAR)
