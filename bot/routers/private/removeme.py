from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext
from sqlalchemy.orm import selectinload

from bot.keyboards.groups import SelectGroup, select_remove_group
from bot.models import User
from bot.repositories.group import GroupFilter
from bot.repositories.uow import UnitOfWork
from bot.repositories.user import UserFilter


async def select_remove(message: Message, uow: UnitOfWork, i18n: I18nContext) -> None:
    user = await uow.users.find_one(UserFilter(id=message.from_user.id), options=[selectinload(User.groups)])  # type: ignore[union-attr]
    if not user or not user.groups:
        await message.answer(i18n.error.user.notfound())
        return

    await message.answer(
        i18n.private.remove.me(),
        reply_markup=select_remove_group(user.groups, i18n),
    )


async def remove_group(
        callback: CallbackQuery,
        bot: Bot,
        uow: UnitOfWork,
        callback_data: SelectGroup,
        i18n: I18nContext
) -> None:
    chat = await bot.get_chat(chat_id=callback_data.chat_id)
    sender = await uow.users.get_user_in_group(
        callback.from_user.id,
        callback_data.chat_id,
        [selectinload(User.groups)]
    )
    if not sender:
        await callback.message.edit_text(i18n.error.user.notin.group())  # type: ignore[union-attr]
        return

    group = await uow.groups.find_one(GroupFilter(id=callback_data.chat_id))
    if not group:
        return
    sender.groups.remove(group)

    await callback.message.edit_text(i18n.private.remove.group(title=chat.title))  # type: ignore[union-attr]


async def remove_all(callback: CallbackQuery, uow: UnitOfWork, i18n: I18nContext) -> None:
    user = await uow.users.find_one(UserFilter(id=callback.from_user.id), options=[selectinload(User.groups)])
    if not user or not user.groups:
        await callback.message.edit_text(i18n.error.user.notfound())  # type: ignore[union-attr]
        return
    await uow.delete(user)
    await callback.message.edit_text(i18n.private.remove.all())  # type: ignore[union-attr]
