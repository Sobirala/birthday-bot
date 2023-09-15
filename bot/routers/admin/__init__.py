from aiogram import F, Router
from aiogram.filters import Command

from bot.routers.admin.add_congratulation import (
    add,
    add_congratulation,
    add_reply_congratulation,
)
from bot.settings import settings
from bot.states.add_congratulation import AddCongratulation

router = Router()
router.message.filter(F.from_user.id.in_(settings.ADMINS))

router.message.register(add, Command("add"))
router.message.register(add_congratulation, AddCongratulation.input, F.document)
router.message.register(add_reply_congratulation, F.reply_to_message.photo)
