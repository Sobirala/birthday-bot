from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.keyboards.groups import SelectGroup, select_remove_group
from bot.models import Group, User


async def select_remove(
        message: Message, session: AsyncSession, i18n: TranslatorRunner
):
    user = (
        await session.scalars(
            select(User)
            .options(selectinload(User.groups))
            .filter(User.user_id == message.from_user.id)
            .limit(1)
        )
    ).first()
    if not user or not user.groups:
        return await message.answer(i18n.error.user.notfound())

    await message.answer(
        i18n.private.remove.me(),
        reply_markup=await select_remove_group(user.groups, i18n),
    )


async def remove_group(
        callback: CallbackQuery,
        bot: Bot,
        session: AsyncSession,
        callback_data: SelectGroup,
        i18n: TranslatorRunner,
):
    try:
        chat = await bot.get_chat(chat_id=callback_data.chat_id)
        sender = (
            await session.scalars(
                select(User)
                .options(selectinload(User.groups))
                .join(User.groups)
                .filter(Group.chat_id == callback_data.chat_id)
                .filter(User.user_id == callback.from_user.id)
                .limit(1)
            )
        ).first()
        if not sender:
            return await callback.message.edit_text(i18n.error.user.notin.group())

        group = (
            await session.scalars(
                select(Group).filter(Group.chat_id == callback_data.chat_id).limit(1)
            )
        ).first()
        sender.groups.remove(group)

        await callback.message.edit_text(i18n.private.remove.group(title=chat.title))
    except TelegramBadRequest:
        logger.error(f"Chat with id {callback_data.chat_id} not found")
        await callback.message.edit_text(
            i18n.error.bot.was.kicked(title=callback_data.title)
        )


async def remove_all(
        callback: CallbackQuery, session: AsyncSession, i18n: TranslatorRunner
):
    sender = (
        await session.scalars(
            select(User)
            .options(selectinload(User.groups))
            .filter(User.user_id == callback.from_user.id)
            .limit(1)
        )
    ).first()
    if not sender or not sender.groups:
        return await callback.message.edit_text(i18n.error.user.notfound())
    await session.delete(sender)
    await callback.message.edit_text(i18n.private.remove.all())
