from asyncio import sleep
from math import inf
from typing import MutableMapping

from aiogram import Bot
from aiogram.types import ChatMemberUpdated, Message
from aiogram_i18n import I18nContext
from cachetools import TTLCache

from bot.keyboards.register import register_keyboard
from bot.models import Group
from bot.repositories.group import GroupFilter
from bot.repositories.uow import UnitOfWork

cache: MutableMapping[int, bool] = TTLCache(maxsize=inf, ttl=10.0)


async def invite_bot(event: ChatMemberUpdated, uow: UnitOfWork, bot: Bot, i18n: I18nContext) -> None:
    await sleep(1)
    if event.chat.id not in cache:
        group = Group(id=event.chat.id, title=event.chat.title)
        await uow.groups.merge(group)
        await bot.send_message(
            chat_id=event.chat.id,
            text=i18n.group.start(),
            reply_markup=await register_keyboard(bot, event.chat.id, i18n)
        )


async def migrate_chat(message: Message, uow: UnitOfWork, bot: Bot, i18n: I18nContext) -> None:
    await uow.groups.update(GroupFilter(id=message.migrate_from_chat_id), id=message.chat.id)
    await message.answer(
        i18n.group.migrate(),
        reply_markup=await register_keyboard(bot, message.chat.id, i18n)
    )
    cache[message.chat.id] = True
