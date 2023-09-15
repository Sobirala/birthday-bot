from itertools import groupby

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram.utils.formatting import Bold, Text, TextLink, as_list
from aiogram_i18n import I18nContext
from babel.core import Locale
from babel.dates import format_datetime
from sqlalchemy.orm import selectinload

from bot.keyboards.groups import SelectGroup, select_calendar_group
from bot.models import Group, User
from bot.repositories.group import GroupFilter
from bot.repositories.uow import UnitOfWork
from bot.repositories.user import UserFilter


async def select_calendar(message: Message, uow: UnitOfWork, i18n: I18nContext) -> None:
    user = await uow.users.find_one(UserFilter(id=message.from_user.id), options=[selectinload(User.groups)])  # type: ignore[union-attr]
    if user and user.groups:
        await message.answer(
            i18n.private.select.calendar(),
            reply_markup=select_calendar_group(user.groups),
        )


async def print_calendar(
        callback: CallbackQuery,
        bot: Bot,
        callback_data: SelectGroup,
        uow: UnitOfWork,
        i18n: I18nContext,
        locale: str
) -> None:
    chat = await bot.get_chat(chat_id=callback_data.chat_id)

    sender = await uow.users.get_user_in_group(callback.from_user.id, callback_data.chat_id)
    if not sender:
        await callback.message.answer(i18n.error.user.notin.group())  # type: ignore[union-attr]
        return

    group = await uow.groups.find_one(GroupFilter(id=callback_data.chat_id),
                                      options=[selectinload(Group.users)])
    if len(group.users) == 1:  # type: ignore[union-attr]
        await callback.message.answer(i18n.warning.only.sender.ingroup())  # type: ignore[union-attr]
        return

    b_locale = Locale.parse(locale)
    months = b_locale.months['stand-alone']['wide']
    message = as_list(
        *(as_list(
            Bold(months[month].title()),
            *(Text(
                TextLink(user.fullname, url=f"tg://user?id={user.user_id}"),
                ", ",
                format_datetime(user.birthday, format='dd MMMM', locale=b_locale)
            ) for user in users),
            sep="\n"
        ) for month, users in groupby(group.users, lambda x: x.birthday.month)),  # type: ignore[union-attr]
        sep="\n\n"
    )
    await callback.message.answer(i18n.private.calendar(title=chat.title) + "\n\n" + message.as_html())  # type: ignore[union-attr]
