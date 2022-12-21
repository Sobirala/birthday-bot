from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, types
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.config import Settings


class GlobalVariables(BaseMiddleware):
    def __init__(self, database: AsyncIOMotorDatabase, config: Settings) -> None:
        self.database = database
        self.config = config

    async def __call__(
            self,
            handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
            event: types.Message,
            data: Dict[str, Any]
    ) -> Any:
        logger.info(event)
        data["config"] = self.config
        data["database"] = self.database
        return await handler(event, data)
