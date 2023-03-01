from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.deep_linking import create_start_link


async def generate_link_button(bot: Bot, chat_id: int):
    link = await create_start_link(bot, payload=str(chat_id))
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Додай свій день народження в календар", url=link
                )
            ]
        ]
    )
