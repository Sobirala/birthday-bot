from typing import Any, Optional, Union, cast

from aiogram.types import User
from aiogram_i18n.managers import BaseManager
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from bot.enums import Language


class RedisManager(BaseManager):
    def __init__(
        self,
        redis: Union["Redis[Any]", ConnectionPool],
        default_locale: Optional[str] = None,
    ):
        super().__init__(default_locale=default_locale)
        if isinstance(redis, ConnectionPool):
            redis = Redis(connection_pool=redis)
        self.redis: "Redis[Any]" = redis

    async def get_locale_by_user_id(self, user_id: int) -> Optional[str]:
        redis_key = f"i18n:{user_id}:locale"
        value = await self.redis.get(redis_key)
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return value

    async def get_locale(self, event_from_user: User) -> str:
        value = await self.get_locale_by_user_id(event_from_user.id)
        if not value and event_from_user.language_code in Language:
            return event_from_user.language_code or cast(str, self.default_locale)
        return value or cast(str, self.default_locale)

    async def set_locale(self, language: str, event_from_user: User) -> None:
        redis_key = f"i18n:{event_from_user.id}:locale"
        await self.redis.set(redis_key, language)
