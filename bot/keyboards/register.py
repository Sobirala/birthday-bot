from aiogram import Bot
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def register_keyboard(chat_id: int, bot: Bot):
    link = await create_start_link(bot, payload=str(chat_id))
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Додай свій день народження в календар", url=link)
    return builder.as_markup()
