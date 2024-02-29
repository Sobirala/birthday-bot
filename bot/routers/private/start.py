from aiogram import Bot, html
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram_i18n import I18nContext


async def start_chat(message: Message, bot: Bot, i18n: I18nContext) -> None:
    await message.answer(
        i18n.private.start(fullname=html.quote(message.from_user.full_name)),  # type: ignore[union-attr]
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text=i18n.buttons.invite.bot(),
                url=f"t.me/{(await bot.me()).username}?startgroup=1",
            )
        ]]),
    )
