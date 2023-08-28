from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner

from bot.keyboards.calendar_widget import Calendar
from bot.keyboards.reset import reset_keyboard
from bot.states.form import Form


async def confirm_reset_user(message: Message, i18n: TranslatorRunner):
    await message.answer(
        i18n.private.reset.user(),
        reply_markup=reset_keyboard(i18n),
    )


async def reset_user(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner, locale: str):
    await state.set_state(Form.birthday)
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        i18n.private.form.birthday(),
        reply_markup=Calendar.generate_keyboard(locale),
    )
