from aiogram import types, Bot, Router, F
from aiogram.utils.deep_linking import create_start_link
from aiogram.filters import Command

from messages.inGroup import *
from buttons import generate_refferal_button

router = Router()

@router.message(F.content_type.in_({types.ContentType.NEW_CHAT_MEMBERS}))
async def check_channel(message: types.Message, bot: Bot):
    bot_id = (await bot.get_me()).id
    link = await create_start_link(bot, payload = str(message.chat.id), encode=True)
    keyboard = await generate_refferal_button(link)
    if message.new_chat_members[0].id == bot_id:
        return await message.answer(FIRST_ADD, parse_mode="HTML", reply_markup=keyboard)
    else:
        return await message.answer(ADD_MEMBER.format(username = message.new_chat_members[0].full_name, id = message.new_chat_members[0].id), parse_mode="HTML", reply_markup=keyboard)

@router.message(Command(commands=["start"]), F.chat.type.in_({"group", "supergroup"}))
async def check_channel(message: types.Message, bot: Bot):
    link = await create_start_link(bot, payload = str(message.chat.id), encode=True)
    keyboard = await generate_refferal_button(link)
    return await message.answer(FIRST_ADD, parse_mode="HTML", reply_markup=keyboard)