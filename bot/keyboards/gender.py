from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fluentogram import TranslatorRunner

from bot.models.enums import Gender


class SelectGender(CallbackData, prefix="gender"):
    gender: Gender


async def gender_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for gender in Gender:
        builder.button(
            text=i18n.gender.names(gender=gender.value),
            callback_data=SelectGender(gender=gender),
        )
    builder.adjust(2)
    return builder.as_markup()
