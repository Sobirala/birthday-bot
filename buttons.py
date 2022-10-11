from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def generate_refferal_button(url: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("➕ Додай свій день народження в календар", url=url)]
    ])