from typing import Any, Awaitable, Callable, Dict, TypeVar
from aiogram import BaseMiddleware, types

class GetDBVariable(BaseMiddleware):
    def  __init__(self, database) -> None:
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
    def  __init__(self, limit=2, key_prefix='antiflood_') -> None:
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

# class ThrottlingMiddleware(BaseMiddleware):
#     """
#     Simple middleware
#     """

#     def __init__(self, limit=2, key_prefix='antiflood_'):
#         self.rate_limit = limit
#         self.prefix = key_prefix
#         super(ThrottlingMiddleware, self).__init__()

#     async def on_process_message(self, message: types.Message, data: dict):
#         """
#         This handler is called when dispatcher receives a message
#         :param message:
#         """
#         # Get current handler
#         handler = current_handler.get()

#         # Get dispatcher from context
#         dispatcher = Dispatcher.get_current()
#         # If handler was configured, get rate limit and key from handler
#         if handler:
#             limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
#             key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
#         else:
#             limit = self.rate_limit
#             key = f"{self.prefix}_message"

#         # Use Dispatcher.throttle method.
#         try:
#             await dispatcher.throttle(key, rate=limit)
#         except Throttled as t:
#             # Execute action
#             await self.message_throttled(message, t)

#             # Cancel current handler
#             raise CancelHandler()

#     async def message_throttled(self, message: types.Message, throttled: Throttled):
#         """
#         Notify user only on first exceed and notify about unlocking only on last exceed
#         :param message:
#         :param throttled:
#         """
#         handler = current_handler.get()
#         dispatcher = Dispatcher.get_current()
#         if handler:
#             key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
#         else:
#             key = f"{self.prefix}_message"

#         # Calculate how many time is left till the block ends
#         delta = throttled.rate - throttled.delta

#         # Prevent flooding
#         if throttled.exceeded_count <= 2:
#             await message.reply('Too many requests! ')

#         # Sleep.
#         await asyncio.sleep(delta)