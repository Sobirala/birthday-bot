from email import message
from typing import Any
from unittest import result
from zoneinfo import ZoneInfo
from aiogram import Bot, types, Router, F
from aiogram.filters import Command, CommandObject, Text
from aiogram.utils.deep_linking import decode_payload
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from datetime import date, datetime
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from geopy.geocoders import GoogleV3
from geopy.adapters import AioHTTPAdapter
from functools import partial
import aiohttp
from babel.dates import format_datetime
import logging

from os import environ
from messages.inPrivate import *
from states import *
from buttons import get_gender_keyboard, get_month_keyboard, submit, confirm_keyboard
from callbacks import NumbersCallbackFactory
from middlewares import Throtled

router = Router()
router.message.filter(F.chat.type.in_({"private"}))
router.message.middleware(Throtled())

MONTHS = {"Січень": {"str": "січня", "number": 1, "days": 31}, 
          "Лютий": {"str": "лютого", "number": 2, "days": 28}, 
          "Березень": {"str": "березня", "number": 3, "days": 31}, 
          "Квітень": {"str": "квітня", "number": 4, "days": 30}, 
          "Травень": {"str": "травня", "number": 5, "days": 31}, 
          "Червень": {"str": "червня", "number": 6, "days": 30}, 
          "Липень": {"str": "липня", "number": 7, "days": 31}, 
          "Серпень": {"str": "серпня", "number": 8, "days": 31}, 
          "Вересень": {"str": "вересня", "number": 9, "days": 30}, 
          "Жовтень": {"str": "жовтня", "number": 10, "days": 31}, 
          "Листопад": {"str": "листопада", "number": 11, "days": 30}, 
          "Грудень": {"str": "грудня", "number": 12, "days": 31}}
GENDERS = {"Ч": "чоловіча", "Ж": "жіноча"}

if environ["DEBUG"] == "1":
    print("DEBUG")

    @router.message(F.chat.func(lambda chat: chat.id == 569355579))
    async def idi_nahui(message: types.Message):
        return message.answer("Йди нахуй!")

    @router.message(F.chat.func(lambda chat: chat.id != int(environ["ADMIN"])))
    async def test(message: types.Message):
        return message.answer("Технічні роботи")

@router.message(Command(commands=["start"]))
async def start(message: types.Message, bot: Bot, state: FSMContext, command: CommandObject, database: Any):
    if command.args:
        group_id = decode_payload(command.args)
        await state.clear()
        await state.update_data({"group_id": group_id})
        group = await database.groups.find_one({"_id": int(group_id)}, {"users": 1})
        if group == None:
            return await message.answer("Такої групи не існує або невірне посилання!")
        chat = await bot.get_chat(group_id)
        for i in group["users"]:
            if i["_id"] == message.chat.id:
                return await message.answer(YET_ADD.format(groupname = chat.title))
        user = await database.users.find_one({"_id": message.chat.id})
        if user != None:
            group_id = decode_payload(command.args)
            chat = await bot.get_chat(group_id)
            await database.users.update_one({"_id": message.chat.id}, {"$push": {"groups": int(group_id)}})
            await database.groups.update_one({"_id": int(group_id)}, {"$push": {"users": {
                "_id": message.chat.id,
                "username": message.chat.full_name,
                "timezone": user["timezone"],
                "birthday":  user["birthday"],
                "birthday_str":  user["birthday_str"]
            }}})
            return await message.answer(SUCCESS_ADD.format(groupname = chat.title), parse_mode="HTML")
        await state.set_state(Form.year)
        await message.answer(ADD.format(groupname = chat.title), parse_mode="HTML")
        return await message.answer(YEAR)
    return await message.answer(START)

@router.message(Command(commands=["help"]))
async def help(message: types.Message):
    return await message.answer(HELP)

@router.message(Command(commands=["reset"]))
async def reset(message: types.Message):
    return await message.answer(RESET, reply_markup=submit)

@router.message(Command(commands=["calendar"]))
async def calendar(message: types.Message, bot: Bot, database: Any):
    user = await database.users.find_one({"_id": message.chat.id})
    if "groups" not in user or len(user["groups"]) == 0:
        return await message.answer("Ви не зареєстровані у жодній групі.")
    builder = InlineKeyboardBuilder()
    for i in user["groups"]:
        chat = await bot.get_chat(i)
        builder.button(text=chat.title, callback_data=NumbersCallbackFactory(action="calendar", value=i))
    builder.adjust(1)
    return await message.answer("Test", reply_markup=builder.as_markup())

@router.callback_query(Text("submit"))
async def submit_change(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    await state.set_state(Form.year)
    await state.update_data(update = True)
    await bot.send_message(callback.from_user.id, YEAR, reply_markup=ReplyKeyboardRemove())

@router.callback_query(NumbersCallbackFactory.filter(F.action == "calendar"))
async def print_dates(callback: types.CallbackQuery, database: Any, callback_data: NumbersCallbackFactory):
    group = await database.groups.find_one({"_id": callback_data.value})
    result = f"🗓 Дні народження учасників гурту «<b>{group['title']}</b>» та їх годинникові зони:\n"
    temp = ""
    for i in sorted(group["users"], key=lambda x: int(x["birthday"].strftime("%m"))):
        if temp == "" or i["birthday_str"] != temp:
            temp = i["birthday_str"]
            result += f"\n<b>{temp}</b>\n"
        birthday = format_datetime(i["birthday"], "d MMMM", locale="uk_UA")
        result += f'<a href="tg://user?id={i["_id"]}">{i["username"]}</a>, {birthday} [{i["timezone"]}]\n'
        print(i)
    await callback.answer()
    return await callback.message.answer(result, parse_mode="HTML")

@router.message(Form.year)
async def get_year(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or len(message.text) != 4:
        return await message.answer(NOT_YEAR)
    
    age = date.today().year - int(message.text)
    if age >= 0 and age <= 120:
        await state.update_data(year = int(message.text))
        await state.set_state(Form.month)
        return await message.answer(MONTH, reply_markup = (await get_month_keyboard(MONTHS)))
    return await message.answer(NOT_YEAR)

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
    if not all([day.isdigit(), int(day) > 0, int(day) <= MONTHS[data["month"]]["days"]]):
        return await message.answer(NOT_DAY)
    await state.update_data(day = int(message.text))
    await state.set_state(Form.gender)
    return await message.answer(GENDER, reply_markup= (await get_gender_keyboard(list(GENDERS.keys()))))

@router.message(Form.gender)
async def get_gender(message: types.Message, state: FSMContext):
    gender = message.text
    if gender not in GENDERS.keys():
        return await message.answer(NOT_GENDER)
    await state.update_data(gender = GENDERS[message.text])
    await state.set_state(Form.confirm)

    data = await state.get_data()
    return await message.answer(SUCCESS_USER.format(birthday = format_datetime(datetime(data["year"], MONTHS[data["month"]]["number"], data["day"]), "d MMMM, yyyy", locale="uk_UA"), gender=data["gender"]), reply_markup=confirm_keyboard)

@router.message(Form.town)
async def get_town(message: types.Message, state: FSMContext):
    API_TOKEN = environ["GOOGLE_TOKEN"]
    async with GoogleV3(
        api_key=API_TOKEN,
        user_agent="birthday_bot",
        adapter_factory=AioHTTPAdapter,
    ) as geolocator:
        geocode = partial(geolocator.geocode, language="uk")
        address = await geocode(message.text)
    if address == None:
        return await message.answer(NOT_TOWN, reply_markup=ReplyKeyboardRemove())
    await state.update_data(town = address.address)
    url = "http://timezonefinder.michelfe.it/api/{}_{}_{}".format(0, address.longitude, address.latitude)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            try:
                tz_info = await response.json(content_type='application/javascript')
                today = datetime.today().replace(tzinfo=ZoneInfo(tz_info['tz_name']))
                date = format_datetime(today, "d MMMM Y", locale='uk_UA')
                time = format_datetime(today, "H:mm")
            except Exception as e:
                logging.error(e)
                date = "ERROR"
                time = "ERROR"
    await state.update_data({"timezone": tz_info["tz_name"]})
    await state.set_state(Form.confirm)
    await message.answer(SUCCESS_TOWN.format(address=address, date=date, time=time), reply_markup=confirm_keyboard)

@router.message(Form.confirm)
async def confirm(message: types.Message, state: FSMContext, bot: Bot, database: Any):
    if message.text not in ['Так', 'Ні']:
        return await message.answer(NOT_SUCCESS)
    data = await state.get_data()
    if 'town' in data:
        if message.text == "Ні":
            await state.set_state(Form.town)
            return await message.answer(NOT_SUCCESS_TOWN, reply_markup=ReplyKeyboardRemove())
        user = {
                "_id": message.chat.id,
                "username": message.chat.full_name,
                "gender": data["gender"],
                "address": data["town"],
                "timezone": data["timezone"],
                "birthday": datetime(data["year"], MONTHS[data["month"]]["number"], data["day"]),
                "birthday_str": f"{data['month']}"
            }
        if "update" not in data:
            print(data)
            chat = await bot.get_chat(data["group_id"])
            user["groups"] = [int(data["group_id"])]
            await database.users.insert_one(user)
            await database.groups.update_one({"_id": int(data["group_id"])}, {"$push": {"users": {
                "_id": message.chat.id,
                "username": message.chat.full_name,
                "timezone": data["timezone"],
                "birthday":  datetime(data["year"], MONTHS[data["month"]]["number"], data["day"]),
                "birthday_str": f"{data['month']}"
            }}}, upsert=True)
            return await message.answer(SUCCESS_ADD.format(groupname=chat.title), reply_markup=ReplyKeyboardRemove())
        else:
            await database.users.replace_one({"_id": message.chat.id}, user, upsert = True)
            await database.groups.update_many({"users._id": message.chat.id}, {"$set": {"users.$": {
                "_id": message.chat.id,
                "username": message.chat.full_name,
                "timezone": data["timezone"],
                "birthday": datetime(data["year"], MONTHS[data["month"]]["number"], data["day"]),
                "birthday_str": f"{data['month']}"
            }}})
            return await message.answer("Ваші дані оновлено.", reply_markup=ReplyKeyboardRemove())
    elif 'gender' in data:
        if message.text == "Ні":
            await state.set_state(Form.year)
            return await message.answer(NOT_SUCCESS_USER, reply_markup=ReplyKeyboardRemove())
        await state.set_state(Form.town)
        await message.answer(TOWN, reply_markup=ReplyKeyboardRemove())

