from aiogram.fsm.state import State, StatesGroup

class AddAdminFSM(StatesGroup):
    waiting_for_user_input = State()  # ожидаем ID или username для добавления админа

class RemoveAdminFSM(StatesGroup):
    waiting_for_user_id = State()     # ожидаем ID или username для удаления админа
