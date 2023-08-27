from aiogram.types import ChatMemberUpdated

from bot.repositories.group import GroupFilter
from bot.repositories.uow import UnitOfWork


async def kick_bot(event: ChatMemberUpdated, uow: UnitOfWork):
    await uow.groups.delete(GroupFilter(chat_id=event.chat.id))
