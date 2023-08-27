from aiogram import F, Router
from aiogram.enums.chat_type import ChatType
from aiogram.filters import Command, CommandStart, StateFilter

from bot.keyboards.calendar_widget import SelectDate
from bot.keyboards.confirm import SelectConfirm
from bot.keyboards.gender import SelectGender
from bot.keyboards.groups import SelectGroup
from bot.states.form import Form
from .calendar import print_calendar, select_calendar
from .form import (
    confirm_address,
    confirm_birthday,
    input_address,
    input_birthday,
    input_gender,
    remove_extra,
    start_form,
)
from .removeme import remove_all, remove_group, select_remove
from .reset import confirm_reset_user, reset_user
from .start import start_chat
from bot.enums import GroupActions

router = Router()
router.message.filter(F.chat.type == ChatType.PRIVATE)

router.message.register(start_form, CommandStart(magic=F.args))
router.callback_query.register(input_birthday, Form.birthday, SelectDate.filter())
router.callback_query.register(input_gender, Form.gender, SelectGender.filter())
router.callback_query.register(
    confirm_birthday, Form.confirm_birthday, SelectConfirm.filter()
)
router.message.register(input_address, Form.address)
router.callback_query.register(
    confirm_address, Form.confirm_address, SelectConfirm.filter()
)

router.message.register(remove_extra, StateFilter(Form))

router.message.register(start_chat, CommandStart())

router.message.register(confirm_reset_user, Command("reset"))
router.callback_query.register(reset_user, F.data == "reset_user")

router.message.register(select_calendar, Command("calendar"))
router.callback_query.register(
    print_calendar, SelectGroup.filter(F.action == GroupActions.CALENDAR)
)

router.message.register(select_remove, Command("removeme"))
router.callback_query.register(
    remove_group, SelectGroup.filter(F.action == GroupActions.REMOVE)
)
router.callback_query.register(remove_all, F.data == "remove_all")
