from aiogram import Router

from bot.routers.group import router as group_router
from bot.routers.private import router as private_router

router = Router()

router.include_router(group_router)
router.include_router(private_router)
