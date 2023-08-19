from aiogram.types import Message
from fluentogram import TranslatorRunner
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Group
from bot.repositories.group import GroupFilter
from bot.repositories.uow import UnitOfWork


async def collect(message: Message, uow: UnitOfWork, i18n: TranslatorRunner):
    group = await uow.groups.find_one(GroupFilter(chat_id=message.chat.id))
    if group:
        group.collect = not group.collect
        await message.answer(i18n.group.collect(collect=group.collect))
