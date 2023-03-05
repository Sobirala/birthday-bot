from enum import Enum
from typing import List

from aiogram.filters.callback_data import CallbackData
from aiogram.methods import GetChat
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fluentogram import TranslatorRunner
from loguru import logger

from bot.models import Group


class GroupActions(Enum):
    CALENDAR = "calendar"
    REMOVE = "remove"


class SelectGroup(CallbackData, prefix="group"):
    action: GroupActions
    chat_id: int
    title: str


async def _build_group_keyboard(
        builder: InlineKeyboardBuilder, groups: List[Group], action: GroupActions
):
    for group in groups:
        with logger.catch(message=f"Group with chat id {group.chat_id} not found"):
            chat = await GetChat(chat_id=group.chat_id)
            builder.button(
                text=chat.title,
                callback_data=SelectGroup(
                    action=action, chat_id=group.chat_id, title=chat.title
                ),
            )
    builder.adjust(2)


async def select_calendar_group(groups: List[Group]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    await _build_group_keyboard(builder, groups, GroupActions.CALENDAR)

    return builder.as_markup()


async def select_remove_group(
        groups: List[Group], i18n: TranslatorRunner
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    await _build_group_keyboard(builder, groups, GroupActions.REMOVE)
    builder.row(
        InlineKeyboardButton(text=i18n.buttons.remove.all(), callback_data="remove_all")
    )

    return builder.as_markup()
