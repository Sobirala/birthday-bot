from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bot.repositories.uow import UnitOfWork


class SessionMaker(BaseMiddleware):
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self._async_sessionmaker = sessionmaker

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        async with self._async_sessionmaker() as session:
            async with session.begin():
                async with UnitOfWork(session) as uow:
                    data["uow"] = uow
                    return await handler(event, data)
