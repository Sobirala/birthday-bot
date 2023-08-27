from aiogram.types import Message
from fluentogram import TranslatorRunner

from bot.keyboards.donate import donate_keyboard


async def donate(message: Message, i18n: TranslatorRunner):
    await message.answer(
        i18n.donate(),
        reply_markup=donate_keyboard(i18n)
    )
