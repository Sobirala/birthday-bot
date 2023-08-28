from aiogram import Bot
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fluentogram import TranslatorRunner


async def register_keyboard(bot: Bot, chat_id: int, i18n: TranslatorRunner):
    link = await create_start_link(bot, payload=str(chat_id))
    builder = InlineKeyboardBuilder()
    builder.button(text=i18n.buttons.add.birthday(), url=link)
    return builder.as_markup()
