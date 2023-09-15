from aiogram.types import ChatMemberUpdated

from bot.repositories.group import GroupFilter
from bot.repositories.uow import UnitOfWork


async def kick_bot(event: ChatMemberUpdated, uow: UnitOfWork) -> None:
    await uow.groups.delete(GroupFilter(id=event.chat.id))
