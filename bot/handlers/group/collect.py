from aiogram.types import Message
from fluentogram import TranslatorRunner
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Group


async def collect(message: Message, session: AsyncSession, i18n: TranslatorRunner):
    group = (
        await session.scalars(
            select(Group).filter(Group.chat_id == message.chat.id).limit(1)
        )
    ).first()
    if group:
        group.collect = not group.collect
        await message.answer(i18n.group.collect(collect=group.collect))
