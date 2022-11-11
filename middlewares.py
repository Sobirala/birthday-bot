import logging
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware, types


class ConfigVariables(BaseMiddleware):
    def __init__(self, database) -> None:
        self.database = database

    async def __call__(
            self,
            handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
            event: types.Message,
            data: Dict[str, Any]
    ) -> Any:
        logging.debug(event)
        data['database'] = self.database
        return await handler(event, data)
