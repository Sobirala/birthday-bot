from typing import Union

from aiogram.filters.callback_data import CallbackData


class NumbersCallbackFactory(CallbackData, prefix="fabnum"):
    action: str
    value: Union[int, str]
