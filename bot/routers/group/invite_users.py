from asyncio import sleep

from aiogram import Bot
from aiogram.types import Message
from fluentogram import TranslatorRunner

from bot.keyboards.register import register_keyboard


async def invite_users(message: Message, bot: Bot, i18n: TranslatorRunner):
    link = await register_keyboard(bot, message.chat.id, i18n)
    for user in filter(lambda new_member: not new_member.is_bot, message.new_chat_members):
        await message.answer(i18n.group.new.member(mention=user.mention_html()), reply_markup=link)
        await sleep(0.1)
