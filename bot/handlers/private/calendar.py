import calendar
from itertools import groupby

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from babel.core import Locale
from babel.dates import format_datetime
from fluentogram import TranslatorRunner
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.keyboards.groups import SelectGroup, select_calendar_group
from bot.models import Group, User


async def select_calendar(
        message: Message, session: AsyncSession, i18n: TranslatorRunner
):
    user = (
        await session.scalars(
            select(User)
            .filter(User.user_id == message.from_user.id)
            .options(selectinload(User.groups))
            .limit(1)
        )
    ).first()
    if user and user.groups:
        await message.answer(
            i18n.private.select.calendar(),
            reply_markup=await select_calendar_group(user.groups),
        )


async def print_calendar(
        callback: CallbackQuery,
        bot: Bot,
        callback_data: SelectGroup,
        session: AsyncSession,
        i18n: TranslatorRunner,
        locale: str,
):
    try:
        chat = await bot.get_chat(chat_id=callback_data.chat_id)
        sender = (
            await session.scalars(
                select(User.id)
                .join(User.groups)
                .filter(Group.chat_id == callback_data.chat_id)
                .filter(User.user_id == callback.from_user.id)
                .limit(1)
            )
        ).first()
        if not sender:
            return await callback.message.answer(i18n.error.user.notin.group())

        users = (
            await session.scalars(
                select(User)
                .select_from(Group)
                .join(Group.users)
                .filter(Group.chat_id == callback_data.chat_id)
                .order_by(
                    func.date_part("month", User.birthday),
                    func.date_part("day", User.birthday),
                )
            )
        ).all()
        if len(users) == 1:
            return await callback.message.answer(i18n.warning.only.sender.ingroup())

        message = f"{i18n.private.calendar(title=chat.type)}\n\n"
        c = calendar.LocaleTextCalendar(calendar.MONDAY, (locale, None))
        for month, group in groupby(users, lambda x: x.birthday.month):
            message += f"{c.formatmonthname(theyear=2023, themonth=month, width=10, withyear=False).strip().title()}\n"
            for user in group:
                message += "<a href='tg://user?id={id}'>{fullname}</a>, {birthday}\n".format(
                    id=user.user_id,
                    fullname=user.fullname,
                    birthday=format_datetime(user.birthday, format='dd MMMM', locale=Locale.parse(locale, sep='-'))
                )
            message += "\n"
        await callback.message.answer(message)
    except TelegramBadRequest:
        logger.error(f"Chat with id {callback_data.chat_id} not found")
        await callback.message.answer(
            i18n.error.bot.was.kicked(title=callback_data.title)
        )
