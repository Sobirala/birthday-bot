from aiogram import Bot
from aiogram.types import Message
from fluentogram import TranslatorRunner


async def commands(message: Message, bot: Bot, i18n: TranslatorRunner):
    await message.answer(i18n.group.commands(url=(await bot.me()).url))
