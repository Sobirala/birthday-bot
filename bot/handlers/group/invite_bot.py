from asyncio import sleep
from math import inf

from aiogram import Bot
from aiogram.methods import SendMessage
from aiogram.types import ChatMemberUpdated, Message
from cachetools import TTLCache
from fluentogram import TranslatorRunner
from sqlalchemy import update
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Group
from bot.utils.links import generate_link_button

cache = TTLCache(maxsize=inf, ttl=10.0)


async def invite_bot(
        event: ChatMemberUpdated, session: AsyncSession, bot: Bot, i18n: TranslatorRunner
):
    await sleep(1)
    if event.chat.id not in cache:
        await session.execute(
            insert(Group)
            .values(chat_id=event.chat.id, title=event.chat.title)
            .on_conflict_do_update(
                index_elements=[Group.chat_id], set_=dict(title=event.chat.title)
            )
        )
        await SendMessage(
            chat_id=event.chat.id,
            text=i18n.group.start(),
            reply_markup=await generate_link_button(bot, event.chat.id),
        )


async def migrate_chat(
        message: Message, session: AsyncSession, bot: Bot, i18n: TranslatorRunner
):
    await session.execute(
        update(Group)
        .where(Group.chat_id == message.migrate_from_chat_id)
        .values(chat_id=message.chat.id)
    )
    await message.answer(
        i18n.group.migrate(),
        reply_markup=await generate_link_button(bot, message.chat.id),
    )
    cache[message.chat.id] = True
