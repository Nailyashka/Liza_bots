from aiogram.fsm.state import State, StatesGroup

class OrderForm(StatesGroup):
    color = State()
    lining = State()
    lining_text = State()
    comment = State()
    city = State()
    contact = State()
