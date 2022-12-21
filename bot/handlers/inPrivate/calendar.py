from aiogram import Bot, types, Router, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.callbacks import NumbersCallbackFactory
from bot.messages.inPrivate import *

router = Router()


@router.message(Command(commands=["calendar"]))
async def calendar(message: types.Message, bot: Bot, database: AsyncIOMotorDatabase):
    user = await database.users.find_one({"_id": message.chat.id})
    if user is None:
        return await message.answer("Ви не зареєстровані у боті")
    if "groups" not in user or len(user["groups"]) == 0:
        return await message.answer("Ви не зареєстровані у жодній групі.")
    builder = InlineKeyboardBuilder()
    for i in user["groups"]:
        chat = await bot.get_chat(i)
        builder.button(text=chat.title, callback_data=NumbersCallbackFactory(action="calendar", value=i))
    builder.adjust(2)
    return await message.answer("Оберіть групу:", reply_markup=builder.as_markup())


@router.callback_query(NumbersCallbackFactory.filter(F.action == "calendar"))
async def print_dates(callback: types.CallbackQuery, database: AsyncIOMotorDatabase,
                      callback_data: NumbersCallbackFactory, bot: Bot):
    groupname = (await bot.get_chat(callback_data.value)).title
    group = database.groups.aggregate([
        {"$match": {"_id": callback_data.value}},
        {"$unwind": "$users"},
        {
            "$replaceRoot": {
                "newRoot": "$users"
            }
        },
        {"$project": {
            "_id": 1,
            "fullname": 1,
            "timezone": 1,
            "birthday": 1,
            "birthday_str": 1,
            "day": {"$dayOfMonth": "$birthday"}
        }},
        {"$sort": {"day": 1}},
        {"$group": {
            "_id": {"month_str": "$birthday_str", "month": {"$month": "$birthday"}},
            "users": {"$push": "$$ROOT"}
        }},
        {"$sort": {"_id.month": 1}}
    ])
    await callback.answer()
    return await callback.message.answer(await CALENDAR.render_async(groupname=groupname, group=group))
