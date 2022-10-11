from typing import Any, Awaitable, Callable, Dict, TypeVar
from aiogram import BaseMiddleware
from aiogram.types import Message

class GetDBVariable(BaseMiddleware):
    def  __init__(self, database) -> None:
        self.database = database

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        data['database'] = self.database
        return await handler(event, data)