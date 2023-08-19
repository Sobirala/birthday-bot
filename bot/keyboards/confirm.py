from enum import Enum

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fluentogram import TranslatorRunner


class ConfirmTypes(Enum):
    YES = "yes"
    NO = "no"


class SelectConfirm(CallbackData, prefix="confirm"):
    selected: ConfirmTypes


def confirm_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for i in ConfirmTypes:
        builder.button(
            text=i18n.confirm(confirm=i.value), callback_data=SelectConfirm(selected=i)
        )
    builder.adjust(2)
    return builder.as_markup()
