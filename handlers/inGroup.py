from aiogram import types, Bot, Router, F
from aiogram.utils.deep_linking import create_start_link, decode_payload
from messages.inGroup import *
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.message(F.content_type.in_({types.ContentType.NEW_CHAT_MEMBERS})) #, types.ContentType.LEFT_CHAT_MEMBER
async def check_channel(message: types.Message, bot: Bot):
    bot_id = (await bot.get_me()).id
    link = await create_start_link(bot, payload = str(message.chat.id))
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text = "Нажми меня",
        url = link
    ))
    if message.new_chat_members[0].id == bot_id:
        await message.answer(FIRST_ADD, parse_mode="HTML", reply_markup=builder.as_markup())
    else:
        await message.answer(ADD_MEMBER.format(username = message.new_chat_members[0].full_name, id = message.new_chat_members[0].id), parse_mode="HTML", reply_markup=builder.as_markup())