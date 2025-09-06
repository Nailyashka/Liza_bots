# keyboards/menu_keyboards.py
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from keyboards.inline import MenuCallBack

def build_product_keyboard(level: int, menu_name: str, page: int, has_previous: bool, has_next: bool, product_id: int):
    """
    Строим клавиатуру для карточки товара.
    """
    keyboard = InlineKeyboardBuilder()
    buttons_navigation = []

    # Кнопки "Назад" и "Вперёд"
    if has_previous:
        buttons_navigation.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=MenuCallBack(level=level, menu_name=menu_name, page=page - 1).pack()
            )
        )

    if has_next:
        buttons_navigation.append(
            InlineKeyboardButton(
                text="Листай каталог ➡️",
                callback_data=MenuCallBack(level=level, menu_name=menu_name, page=page + 1).pack()
            )
        )

    if buttons_navigation:
        keyboard.row(*buttons_navigation)

    # Кнопка "Заказать"
    keyboard.row(
        InlineKeyboardButton(
            text="📝 Заказать",
            callback_data=MenuCallBack(level=5, menu_name="confirm", product_id=product_id).pack()
        )
    )

    return keyboard.as_markup()
