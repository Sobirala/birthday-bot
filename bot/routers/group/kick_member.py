from aiogram.types import Message
from sqlalchemy.orm import selectinload

from bot.models import User
from bot.repositories.group import GroupFilter
from bot.repositories.uow import UnitOfWork
from bot.repositories.user import UserFilter


async def kick_member(message: Message, uow: UnitOfWork):
    user = await uow.users.find_one(UserFilter(user_id=message.left_chat_member.id),
                                    options=[selectinload(User.groups)])
    if user:
        group = await uow.groups.find_one(GroupFilter(chat_id=message.chat.id))
        user.groups.remove(group)
