from aiogram.filters.callback_data import CallbackData
from typing import Union


class NumbersCallbackFactory(CallbackData, prefix="fabnum"):
    action: str
    value: Union[int, str]
