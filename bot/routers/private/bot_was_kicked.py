from aiogram import html
from aiogram.types import ErrorEvent, Message
from aiogram_i18n import I18nContext

from bot.keyboards.groups import SelectGroup


async def bot_was_kicked(event: ErrorEvent, message: Message, i18n: I18nContext, callback_data: SelectGroup) -> None:
    await message.edit_text(i18n.error.bot.was.kicked(title=html.quote(callback_data.title)))
