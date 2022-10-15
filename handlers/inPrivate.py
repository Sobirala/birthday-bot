from typing import Any
from aiogram import Bot, types, Router, F
from aiogram.filters import Command, CommandObject, Text
from aiogram.utils.deep_linking import decode_payload
from aiogram.fsm.context import FSMContext
from datetime import date
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove

from messages.inPrivate import *
from states import *
from buttons import get_gender_keyboard, get_month_keyboard, submit
from middlewares import Throtled

router = Router()
router.message.filter(F.chat.type.in_({"private"}))
router.message.middleware(Throtled())

MONTHS = {"Січень": {"number": 1, "days": 31}, 
          "Лютий": {"number": 2, "days": 28}, 
          "Березень": {"number": 3, "days": 31}, 
          "Квітень": {"number": 4, "days": 30}, 
          "Травень": {"number": 5, "days": 31}, 
          "Червень": {"number": 6, "days": 30}, 
          "Липень": {"number": 7, "days": 31}, 
          "Серпень": {"number": 8, "days": 31}, 
          "Вересень": {"number": 9, "days": 30}, 
          "Жовтень": {"number": 10, "days": 31}, 
          "Листопад": {"number": 11, "days": 30}, 
          "Грудень": {"number": 12, "days": 31}}
GENDERS = ["Ч", "Ж", "Підрила"]

@router.message(Command(commands=["start"]))
async def start(message: types.Message, bot: Bot, state: FSMContext, command: CommandObject):
    if command.args:
        await state.set_state(Form.year)
        group_id = decode_payload(command.args)
        await state.update_data({"group_id": group_id})
        chat = await bot.get_chat(group_id)
        await message.answer(ADD.format(groupname = chat.title), parse_mode="HTML")
        await message.answer(YEAR)
        return

@router.message(Command(commands=["help"]))
async def help(message: types.Message):
    return await message.answer(HELP)

@router.message(Command(commands=["reset"]))
async def reset(message: types.Message):
    return await message.answer(RESET, reply_markup=submit)

@router.callback_query(Text("submit"))
async def submit_change(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    await state.set_state(Form.year)
    await bot.send_message(callback.from_user.id, YEAR, reply_markup=ReplyKeyboardRemove())

@router.message(Form.year)
async def get_year(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or len(message.text) != 4:
        return await message.answer(NOT_YEAR)
    
    age = date.today().year - int(message.text)
    if age >= 0 and age <= 120:
        await state.update_data(year = message.text)
        await state.set_state(Form.month)
        return await message.answer(MONTH, reply_markup = (await get_month_keyboard(MONTHS)))

@router.message(Form.month)
async def get_month(message: types.Message, state: FSMContext):
    if message.text not in MONTHS:
        return await message.answer(NOT_MONTH)
    await state.update_data(month = message.text)
    await state.set_state(Form.day)
    return await message.answer(DAY, reply_markup=ReplyKeyboardRemove())

@router.message(Form.day)
async def get_day(message: types.Message, state: FSMContext):
    day = message.text
    data = await state.get_data()
    print(day.isdigit(), int(day) > 0, int(day) <= MONTHS[data["month"]]["days"])
    if not any([day.isdigit(), int(day) > 0, int(day) <= MONTHS[data["month"]]["days"]]):
        return await message.answer(NOT_DAY)
    await state.update_data(day = message.text)
    await state.set_state(Form.gender)
    return await message.answer(GENDER, reply_markup= (await get_gender_keyboard(GENDERS)))

@router.message(Form.gender)
async def get_gender(message: types.Message, state: FSMContext):
    gender = message.text
    if gender not in GENDERS:
        return await message.answer(NOT_GENDER)
    await state.update_data(gender = message.text)
    await state.set_state(Form.town)
    await message.answer(TOWN, reply_markup=ReplyKeyboardRemove())

@router.message(Form.town)
async def get_town(message: types.Message, state: FSMContext):
    await state.update_data(town = message.text)
    await state.set_state(Form.confirmation)
