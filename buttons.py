from typing import List
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

async def generate_refferal_button(url: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = "➕ Додай свій день народження в календар", url=url)]
    ])

async def get_month_keyboard(months: List[str]):
    builder = ReplyKeyboardBuilder()
    for i in months:
        builder.add(KeyboardButton(text=str(i)))
    builder.adjust(4)
    return builder.as_markup(resize_keyboard=True)

async def get_gender_keyboard(genders: List[str]):
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text = genders[0]),
        KeyboardButton(text = genders[1])
    )
    builder.row(
        KeyboardButton(text = genders[2])
    )
    return builder.as_markup(resize_keyboard=True)