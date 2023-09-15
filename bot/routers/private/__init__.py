from aiogram import F, Router
from aiogram.enums.chat_type import ChatType
from aiogram.filters import Command, CommandStart

from bot.enums import GroupActions
from bot.keyboards.groups import SelectGroup

from .calendar import print_calendar, select_calendar
from .form import form, start_form
from .removeme import remove_all, remove_group, select_remove
from .reset import confirm_reset_user, reset_user
from .start import start_chat

router = Router()
router.message.filter(F.chat.type == ChatType.PRIVATE)

router.message.register(start_chat, CommandStart(magic=~F.args))
router.message.register(start_form, CommandStart(magic=F.args.cast(int).as_("chat_id")))
router.include_router(form)

router.message.register(select_calendar, Command("calendar"))
router.message.register(select_remove, Command("removeme"))

router.message.register(reset_user, Command("reset"))
router.callback_query.register(confirm_reset_user, F.data == "reset_user")

router.callback_query.register(print_calendar, SelectGroup.filter(F.action == GroupActions.CALENDAR))

router.callback_query.register(remove_group, SelectGroup.filter(F.action == GroupActions.REMOVE))
router.callback_query.register(remove_all, F.data == "remove_all")
