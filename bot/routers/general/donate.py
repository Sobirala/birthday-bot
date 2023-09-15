from aiogram.types import Message
from aiogram_i18n import I18nContext

from bot.keyboards.donate import donate_keyboard


async def donate(message: Message, i18n: I18nContext) -> None:
    await message.answer(
        i18n.donate.me(),
        reply_markup=donate_keyboard(i18n)
    )
