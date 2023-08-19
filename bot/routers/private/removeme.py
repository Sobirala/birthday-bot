from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.keyboards.groups import SelectGroup, select_remove_group
from bot.models import Group, User
from bot.repositories.group import GroupFilter
from bot.repositories.uow import UnitOfWork
from bot.repositories.user import UserFilter


async def select_remove(message: Message, uow: UnitOfWork, i18n: TranslatorRunner):
    user = await uow.users.find_one(UserFilter(user_id=message.from_user.id), options=[selectinload(User.groups)])
    if not user or not user.groups:
        return await message.answer(i18n.error.user.notfound())

    await message.answer(
        i18n.private.remove.me(),
        reply_markup=await select_remove_group(user.groups, i18n),
    )


async def remove_group(
        callback: CallbackQuery,
        bot: Bot,
        uow: UnitOfWork,
        callback_data: SelectGroup,
        i18n: TranslatorRunner
):
    try:
        chat = await bot.get_chat(chat_id=callback_data.chat_id)
        sender = await uow.users.get_user_in_group(callback.from_user.id, callback_data.chat_id, [selectinload(User.groups)])
        if not sender:
            return await callback.message.edit_text(i18n.error.user.notin.group())

        group = await uow.groups.find_one(GroupFilter(chat_id=callback_data.chat_id))
        sender.groups.remove(group)

        await callback.message.edit_text(i18n.private.remove.group(title=chat.title))
    except TelegramBadRequest:
        await callback.message.edit_text(
            i18n.error.bot.was.kicked(title=callback_data.title)
        )


async def remove_all(callback: CallbackQuery, uow: UnitOfWork, i18n: TranslatorRunner):
    user = await uow.users.find_one(UserFilter(user_id=callback.from_user.id))
    if not user or not user.groups:
        return await callback.message.edit_text(i18n.error.user.notfound())
    await uow.delete(user)
    await callback.message.edit_text(i18n.private.remove.all())
