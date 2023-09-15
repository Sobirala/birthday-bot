from aiogram.filters import Filter
from aiogram.types import Message
from aiogram_i18n import I18nContext


class IsChatAdmin(Filter):
    async def __call__(self, message: Message, i18n: I18nContext) -> bool:
        admins = await message.chat.get_administrators()
        if message.from_user not in admins:
            await message.answer(i18n.error.access.denied())
            return False
        return True
