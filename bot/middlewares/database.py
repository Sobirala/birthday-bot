from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Update
from sqlalchemy.ext.asyncio import async_sessionmaker


class SessionMaker(BaseMiddleware):
    _async_sessionmaker: async_sessionmaker

    def __init__(self, sessionmaker):
        self._async_sessionmaker = sessionmaker

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        async with self._async_sessionmaker() as session:
            async with session.begin():
                data["session"] = session
                return await handler(event, data)
