from typing import List

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def generate_referral_button(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додай свій день народження в календар", url=url)]
    ])


async def get_month_keyboard(months: List[str]) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for i in months:
        builder.add(KeyboardButton(text=str(i)))
    builder.adjust(4)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


async def get_gender_keyboard(genders: List[str]) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for gender in genders:
        builder.button(text=gender)
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


submit = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Змінити дані", callback_data="submit")]
])

confirm_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Так"), KeyboardButton(text="Ні")]
], resize_keyboard=True, one_time_keyboard=True)
