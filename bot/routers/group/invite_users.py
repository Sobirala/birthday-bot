from asyncio import sleep

from aiogram import Bot
from aiogram.types import Message
from aiogram_i18n import I18nContext

from bot.keyboards.register import register_keyboard


async def invite_users(message: Message, bot: Bot, i18n: I18nContext) -> None:
    link = await register_keyboard(bot, message.chat.id, i18n)
    for new_member in message.new_chat_members or []:
        if new_member.is_bot:
            continue
        await message.answer(i18n.group.new.member(mention=new_member.mention_html()), reply_markup=link)
        await sleep(0.1)
