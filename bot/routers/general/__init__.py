from aiogram import Router
from aiogram.filters import Command

from bot.routers.general.donate import donate

router = Router()

router.message.register(donate, Command("donate"))
