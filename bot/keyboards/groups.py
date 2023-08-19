from enum import Enum
from typing import List

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fluentogram import TranslatorRunner

from bot.models import Group


class GroupActions(Enum):
    CALENDAR = "calendar"
    REMOVE = "remove"


class SelectGroup(CallbackData, prefix="group"):
    action: GroupActions
    chat_id: int
    title: str


def _build_group_keyboard(builder: InlineKeyboardBuilder, groups: List[Group], action: GroupActions):
    for group in groups:
        builder.button(
            text=group.title,
            callback_data=SelectGroup(action=action, chat_id=group.chat_id, title=group.title)
        )
    builder.adjust(2)


def select_calendar_group(groups: List[Group]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    _build_group_keyboard(builder, groups, GroupActions.CALENDAR)

    return builder.as_markup()


def select_remove_group(groups: List[Group], i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    _build_group_keyboard(builder, groups, GroupActions.REMOVE)
    builder.row(
        InlineKeyboardButton(text=i18n.buttons.remove.all(), callback_data="remove_all")
    )

    return builder.as_markup()
