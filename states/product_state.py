from aiogram.fsm.state import StatesGroup, State

class ProductForm(StatesGroup):
    name = State()
    description = State()
    photo = State()


class ProductEdit(StatesGroup):
    name = State()