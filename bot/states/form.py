from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    birthday = State()
    gender = State()
    confirm_birthday = State()

    address = State()
    confirm_address = State()
