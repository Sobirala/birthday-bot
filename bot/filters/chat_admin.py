from aiogram.filters import Filter
from aiogram.types import Message
from fluentogram import TranslatorRunner


class IsChatAdmin(Filter):
    async def __call__(self, message: Message, i18n: TranslatorRunner) -> bool:
        admins = await message.chat.get_administrators()
        if message.from_user not in admins:
            await message.answer(i18n.error.access.denied())
            return False
        return True
