from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

class MenuCallBack(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    city_id: int | None = None
    category: int | None = None
    page: int = 1
    product_id: int | None = None



def get_user_main_btns(*, level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        '👜 Каталог': 'catalog'
    }

    for text, menu_name in btns.items():
        if menu_name == 'catalog':
            # Кнопка аренды ведёт на выбор города
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(level=1, menu_name='catalog').pack()
            ))
        else:
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(level=level, menu_name=menu_name).pack()
            ))

    return keyboard.adjust(*sizes).as_markup()
    #мы сформировали все кнопки из словаря
    #а проверки нужны чтоб колбэки с level 'настроить'
    
async def get_products(level: int,
                              menu_name,
                              city_id,
                              category,
                              page,
                              result,
                              sumka,
                              sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    # Пагинация
    if result["has_previous"]:
        keyboard.add(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=MenuCallBack(level=level, menu_name=menu_name, city_id=city_id, category=category, page=page-1).pack()
        ))
    if result["has_next"]:
        keyboard.add(InlineKeyboardButton(
            text="Листай каталог ➡️",
            callback_data=MenuCallBack(level=level, menu_name=menu_name, city_id=city_id, category=category, page=page+1).pack()
        ))
    keyboard.add(InlineKeyboardButton(
        text='📝 Заказать/ Перейти к оформлению',
        callback_data=MenuCallBack(
            level=5,
            menu_name="order",   # любое название
            product_id=sumka.id
        ).pack()

    ))

    return keyboard.adjust(*sizes).as_markup()
        