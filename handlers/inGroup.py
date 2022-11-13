from typing import Any
from aiogram import types, Bot, Router, F
from aiogram.utils.deep_linking import create_start_link
from aiogram.filters import Command

from messages.inGroup import *
from buttons import generate_referral_button

router = Router()
router.message.filter(F.chat.type.in_({"group", "supergroup"}))


@router.message(F.content_type.in_({types.ContentType.NEW_CHAT_MEMBERS}))
async def check_channel(message: types.Message, bot: Bot, database: Any):
    bot_id = (await bot.get_me()).id
    link = await create_start_link(bot, payload=str(message.chat.id), encode=True)
    keyboard = await generate_referral_button(link)
    for new_member in message.new_chat_members:
        if new_member.id == bot_id:
            if (await database.groups.count_documents({"_id": message.chat.id})) == 0:
                await database.groups.insert_one({"_id": message.chat.id, "title": message.chat.title, "users": []})
            await message.answer(FIRST_ADD, parse_mode="HTML", reply_markup=keyboard)
        elif not new_member.is_bot:
            await message.answer(await ADD_MEMBER.render_async(username=new_member.full_name, id=new_member.id),
                                 parse_mode="HTML", reply_markup=keyboard)


@router.message(F.content_type.in_({types.ContentType.LEFT_CHAT_MEMBER}))
async def delete_bot(message: types.Message, bot: Bot, database: Any):
    bot_id = (await bot.get_me()).id
    if message.left_chat_member.id == bot_id:
        await database.groups.delete_one({"_id": message.chat.id})
        await database.users.update_many({}, {"$pull": {"groups": message.chat.id}})
    elif not message.left_chat_member.is_bot:
        await database.groups.update_one({"_id": message.chat.id}, {"$pull": {"users": {"_id": message.left_chat_member.id}}})
        await database.users.update_one({"_id": message.left_chat_member.id}, {"$pull": {"groups": message.chat.id}})


@router.message(Command(commands=["start"]))
async def check_channel(message: types.Message, bot: Bot, database: Any):
    if (await database.groups.count_documents({"_id": message.chat.id})) == 0:
        await database.groups.insert_one({"_id": message.chat.id, "title": message.chat.title, "users": []})
    link = await create_start_link(bot, payload=str(message.chat.id), encode=True)
    keyboard = await generate_referral_button(link)
    return await message.answer(FIRST_ADD, parse_mode="HTML", reply_markup=keyboard)


@router.message(Command(commands=["calendar"]))
async def calendar(message: types.Message, bot: Bot):
    return await message.reply(await NOT_COMMAND.render_async(link=(await bot.get_me()).username), parse_mode="HTML")
