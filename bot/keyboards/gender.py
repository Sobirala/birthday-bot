from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.types import Gender
from fluentogram import TranslatorRunner


class SelectGender(CallbackData, prefix="gender"):
    gender: Gender


def gender_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for gender in Gender:
        builder.button(text=i18n.gender.names(gender=gender), callback_data=SelectGender(gender=gender))
    builder.adjust(2)
    return builder.as_markup()
