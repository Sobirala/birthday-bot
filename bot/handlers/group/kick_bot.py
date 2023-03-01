from aiogram.types import ChatMemberUpdated
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Group


async def kick_bot(event: ChatMemberUpdated, session: AsyncSession):
    group = (
        await session.scalars(
            select(Group).filter(Group.chat_id == event.chat.id).limit(1)
        )
    ).first()
    await session.delete(group)
