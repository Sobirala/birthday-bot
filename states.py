from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    year = State()
    month = State()
    day = State()
    gender = State()
    town = State()