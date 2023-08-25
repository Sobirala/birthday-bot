import calendar
from itertools import groupby

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from babel.core import Locale
from babel.dates import format_datetime
from fluentogram import TranslatorRunner
from sqlalchemy.orm import selectinload

from bot.keyboards.groups import SelectGroup, select_calendar_group
from bot.models import User, Group
from bot.repositories.group import GroupFilter
from bot.repositories.uow import UnitOfWork
from bot.repositories.user import UserFilter


async def select_calendar(message: Message, uow: UnitOfWork, i18n: TranslatorRunner):
    user = await uow.users.find_one(UserFilter(user_id=message.from_user.id), options=[selectinload(User.groups)])
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
        i18n: TranslatorRunner,
        locale: str
):
    try:
        chat = await bot.get_chat(chat_id=callback_data.chat_id)

        sender = await uow.users.get_user_in_group(callback.from_user.id, callback_data.chat_id)
        if not sender:
            return await callback.message.answer(i18n.error.user.notin.group())

        group = await uow.groups.find_one(GroupFilter(chat_id=callback_data.chat_id), options=[selectinload(Group.users)])
        if len(group.users) == 1:
            return await callback.message.answer(i18n.warning.only.sender.ingroup())

        message = f"{i18n.private.calendar(title=chat.title)}\n\n"
        c = calendar.LocaleTextCalendar(calendar.MONDAY, (locale, None))
        for month, users in groupby(group.users, lambda x: x.birthday.month):
            message += f"{c.formatmonthname(theyear=2023, themonth=month, width=10, withyear=False).strip().title()}\n"
            for user in users:
                message += "<a href='tg://user?id={id}'>{fullname}</a>, {birthday}\n".format(
                    id=user.user_id,
                    fullname=user.fullname,
                    birthday=format_datetime(user.birthday, format='dd MMMM', locale=Locale.parse(locale, sep='-'))
                )
            message += "\n"
        await callback.message.answer(message)
    except TelegramBadRequest:
        await callback.message.answer(i18n.error.bot.was.kicked(title=callback_data.title))
