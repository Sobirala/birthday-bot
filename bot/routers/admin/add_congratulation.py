from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_i18n import I18nContext

from bot.enums import Language
from bot.models import Congratulation
from bot.repositories.uow import UnitOfWork
from bot.states.add_congratulation import AddCongratulation


async def add(message: Message, state: FSMContext, i18n: I18nContext) -> None:
    await state.set_state(AddCongratulation.input)
    await message.answer(i18n.congratulation.add())


async def add_congratulation(message: Message, uow: UnitOfWork, locale: Language) -> None:
    await uow.congratulations.create(Congratulation(
        photo_file_id=message.document.file_id,  # type: ignore[union-attr]
        language=locale,
        message=message.html_text
    ))


async def add_reply_congratulation(message: Message, uow: UnitOfWork, locale: Language) -> None:
    await uow.congratulations.create(Congratulation(
        photo_file_id=message.reply_to_message.photo[-1].file_id,  # type: ignore
        language=locale,
        message=message.reply_to_message.html_text  # type: ignore[union-attr]
    ))
