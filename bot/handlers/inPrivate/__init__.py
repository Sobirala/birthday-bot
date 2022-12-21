from aiogram import Router, F

from bot.handlers.inPrivate import form, reset
from bot.handlers.inPrivate import calendar, help, remove

router = Router()
router.message.filter(F.chat.type.in_({"private"}))

router.include_router(form.router)
router.include_router(calendar.router)
router.include_router(reset.router)
router.include_router(remove.router)
router.include_router(help.router)
