from aiogram import Router

from bot.routers.admin import router as admin_router
from bot.routers.general import router as general_router
from bot.routers.group import router as group_router
from bot.routers.private import router as private_router

router = Router()

router.include_router(group_router)
router.include_router(private_router)
router.include_router(admin_router)
router.include_router(general_router)
