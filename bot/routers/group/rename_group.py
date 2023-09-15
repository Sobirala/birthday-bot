from aiogram.types import Message

from bot.repositories.group import GroupFilter
from bot.repositories.uow import UnitOfWork


async def rename_group(message: Message, uow: UnitOfWork) -> None:
    await uow.groups.update(GroupFilter(id=message.chat.id), title=message.new_chat_title)
