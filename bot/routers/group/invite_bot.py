from asyncio import sleep
from math import inf

from aiogram import Bot
from aiogram.types import ChatMemberUpdated, Message
from cachetools import TTLCache
from fluentogram import TranslatorRunner

from bot.keyboards.register import register_keyboard
from bot.models import Group
from bot.repositories.group import GroupFilter
from bot.repositories.uow import UnitOfWork

cache = TTLCache[int, bool](maxsize=inf, ttl=10.0)


async def invite_bot(event: ChatMemberUpdated, uow: UnitOfWork, bot: Bot, i18n: TranslatorRunner):
    await sleep(1)
    if event.chat.id not in cache:
        if not await uow.groups.check_exists(GroupFilter(chat_id=event.chat.id)):
            group = Group(chat_id=event.chat.id, title=event.chat.title)
            await uow.groups.create(group)
        await bot.send_message(
            chat_id=event.chat.id,
            text=i18n.group.start(),
            reply_markup=await register_keyboard(bot, event.chat.id)
        )


async def migrate_chat(message: Message, uow: UnitOfWork, bot: Bot, i18n: TranslatorRunner):
    await uow.groups.update(GroupFilter(chat_id=message.migrate_from_chat_id), chat_id=message.chat.id)
    await message.answer(
        i18n.group.migrate(),
        reply_markup=await register_keyboard(bot, message.chat.id)
    )
    cache[message.chat.id] = True
