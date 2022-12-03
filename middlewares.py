from loguru import logger
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware, types
from config import Settings


class ConfigVariables(BaseMiddleware):
    def __init__(self, database: Any, config: Settings) -> None:
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
