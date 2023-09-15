from aiogram import Bot
from aiogram.types import Message
from aiogram_i18n import I18nContext


async def commands(message: Message, bot: Bot, i18n: I18nContext) -> None:
    await message.answer(i18n.group.commands(url=(await bot.me()).url))
