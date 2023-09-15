from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_i18n import I18nContext

from bot.keyboards.reset import reset_keyboard
from bot.states.form import Form


async def reset_user(message: Message, i18n: I18nContext) -> None:
    await message.answer(i18n.private.reset.user(), reply_markup=reset_keyboard(i18n))


async def confirm_reset_user(callback: CallbackQuery, dialog_manager: DialogManager) -> None:
    await callback.message.edit_reply_markup()  # type: ignore[union-attr]
    await dialog_manager.start(Form.birthday, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND)
