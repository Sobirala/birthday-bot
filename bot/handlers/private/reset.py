from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from fluentogram import TranslatorRunner

from bot.keyboards.calendar_widget import Calendar
from bot.states.form import Form


async def confirm_reset_user(message: Message, i18n: TranslatorRunner):
    await message.answer(
        i18n.private.reset.user(),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=i18n.buttons.reset.user(), callback_data="reset_user"
                    )
                ]
            ]
        ),
    )


async def reset_user(
        callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner, locale: str
):
    await state.set_state(Form.birthday)
    await callback.message.answer(
        i18n.private.form.birthday(),
        reply_markup=await Calendar.generate_keyboard(locale),
    )
