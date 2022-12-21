from aiogram import Bot, types, Router, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.callbacks import NumbersCallbackFactory
from bot.messages.inPrivate import *

router = Router()


@router.message(Command(commands=["removeme"]))
async def removeme(message: types.Message, bot: Bot, database: AsyncIOMotorDatabase):
    user = await database.users.find_one({"_id": message.chat.id})
    if user is None:
        return await message.answer("Ви не зареєстровані у боті")
    if "groups" not in user or len(user["groups"]) == 0:
        return await message.answer("Ви не зареєстровані у жодній групі.")
    builder = InlineKeyboardBuilder()
    for i in user["groups"]:
        with logger.catch(message="Chat not found: "):
            chat = await bot.get_chat(i)
            builder.button(text=chat.title, callback_data=NumbersCallbackFactory(action="remove", value=i).pack())
    builder.button(text="Видалити з усіх груп", callback_data=NumbersCallbackFactory(action="remove", value="all"))
    builder.adjust(2, len(user["groups"]) // 2)
    return await message.answer(REMOVEME, reply_markup=builder.as_markup())


@router.callback_query(NumbersCallbackFactory.filter(F.action == "remove"))
async def remove(callback: types.CallbackQuery, database: AsyncIOMotorDatabase, callback_data: NumbersCallbackFactory,
                 bot: Bot):
    if callback_data.value != "all":
        groupname = (await bot.get_chat(callback_data.value)).title
        await database.groups.update_one({"_id": callback_data.value}, {
            "$pull": {
                "users": {"_id": callback.message.chat.id}
            }
        })
        await database.users.update_one({"_id": callback.message.chat.id}, {
            "$pull": {
                "groups": callback_data.value
            }
        })
        return await callback.message.answer(await REMOVE.render_async(groupname=groupname))
    else:
        await database.groups.update_many({}, {
            "$pull": {
                "users": {"_id": callback.message.chat.id}
            }
        })
        await database.users.delete_one({"_id": callback.message.chat.id})
        return await callback.message.answer(REMOVEALL)
