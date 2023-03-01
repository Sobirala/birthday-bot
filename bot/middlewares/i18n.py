from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update

from bot.translator.hub import Translator


class TranslatorRunnerMiddleware(BaseMiddleware):
    def __init__(self, translator: Translator):
        self.translator = translator

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any],
    ) -> Any:
        data["locale"] = "uk-UA"
        data["i18n"] = self.translator("uk-UA")
        return await handler(event, data)
