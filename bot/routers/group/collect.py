from aiogram.types import Message
from aiogram_i18n import I18nContext

from bot.repositories.group import GroupFilter
from bot.repositories.uow import UnitOfWork


async def collect(message: Message, uow: UnitOfWork, i18n: I18nContext) -> None:
    group = await uow.groups.find_one(GroupFilter(id=message.chat.id))
    if group:
        group.collect = not group.collect
        await message.answer(i18n.group.collect(collect=group.collect))
