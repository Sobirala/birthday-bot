from aiogram.types import Message
from sqlalchemy.orm import selectinload

from bot.models import User
from bot.repositories.group import GroupFilter
from bot.repositories.uow import UnitOfWork
from bot.repositories.user import UserFilter


async def kick_member(message: Message, uow: UnitOfWork) -> None:
    user = await uow.users.find_one(UserFilter(id=message.left_chat_member.id), options=[selectinload(User.groups)])  # type: ignore[union-attr]
    if user:
        group = await uow.groups.find_one(GroupFilter(id=message.chat.id))
        if group:
            user.groups.remove(group)
