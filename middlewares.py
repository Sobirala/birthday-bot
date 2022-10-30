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
        data['database'] = self.database
        return await handler(event, data)


class Throtled(BaseMiddleware):
    def __init__(self, limit=2, key_prefix='antiflood_') -> None:
        self.rate_limit = limit
        self.prefix = key_prefix

    async def __call__(
            self,
            handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
            event: types.Message,
            data: Dict[str, Any]
    ) -> Any:
        print(handler)
        print(event)
        print(data)
        return await handler(event, data)
