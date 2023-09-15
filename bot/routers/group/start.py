from aiogram import Bot
from aiogram.types import Message
from aiogram_i18n import I18nContext

from bot.keyboards.register import register_keyboard
from bot.models import Group
from bot.repositories.uow import UnitOfWork


async def start_group(message: Message, uow: UnitOfWork, bot: Bot, i18n: I18nContext) -> None:
    group = Group(id=message.chat.id, title=message.chat.title)
    await uow.groups.merge(group)

    await message.answer(
        i18n.group.start(),
        reply_markup=await register_keyboard(bot, message.chat.id, i18n),
    )
