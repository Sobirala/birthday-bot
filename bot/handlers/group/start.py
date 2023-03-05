from aiogram import Bot
from aiogram.types import Message
from fluentogram import TranslatorRunner
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Group
from bot.utils.links import generate_link_button


async def start_group(
        message: Message, session: AsyncSession, bot: Bot, i18n: TranslatorRunner
):
    await session.execute(
        insert(Group)
        .values(
            chat_id=message.chat.id,
            title=message.chat.title,
        )
        .on_conflict_do_update(
            index_elements=[Group.chat_id], set_=dict(title=message.chat.title)
        )
    )

    await message.answer(
        i18n.group.start(),
        reply_markup=await generate_link_button(bot, message.chat.id),
    )
