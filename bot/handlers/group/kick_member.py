from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.models import Group, User


async def kick_member(message: Message, session: AsyncSession):
    user = (
        await session.scalars(
            select(User)
            .filter(User.user_id == message.left_chat_member.id)
            .options(selectinload(User.groups))
            .limit(1)
        )
    ).first()
    if user:
        group = (
            await session.scalars(
                select(Group).filter(Group.chat_id == message.chat.id).limit(1)
            )
        ).first()
        user.groups.remove(group)
