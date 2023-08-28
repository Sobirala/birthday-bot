from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fluentogram import TranslatorRunner


def reset_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=i18n.buttons.reset.user(), callback_data="reset_user")
    return builder.as_markup()
