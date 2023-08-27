from aiogram.fsm.state import StatesGroup, State


class AddCongratulation(StatesGroup):
    input = State()
    confirm = State()
