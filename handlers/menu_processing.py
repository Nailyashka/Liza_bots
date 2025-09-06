from venv import logger
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import InputMediaPhoto

from keyboards.menu_keyboards import build_product_keyboard
from orm_query.paginator import UniversalPaginator, pages

from keyboards.inline import  get_user_main_btns
from orm_query.product import get_products_page


async def menu_level_0(session, level, menu_name):
    # просто текст, без баннера
    welcome_text = """
<b>Здравствуйте! 👋</b>
Добро пожаловать в наш бот-каталог <i>изделий ручной работы</i> 👜✨

Здесь вы можете:
🔹 Просмотреть наш ассортимент  
🔹 Выбрать понравившуюся сумку  
🔹 Сделать заказ в пару кликов  
🔹 Задать вопросы мастеру  

Если нужна помощь — просто напишите нам! Мы всегда рады помочь 😊

<b>Начнём? ⬇️</b>
            """
    keyboard_markup = get_user_main_btns(level=level)
    return welcome_text, keyboard_markup



async def menu_level_1(session: AsyncSession, level: int, menu_name: str, page: int = 1):
    per_page = 1
    result = await get_products_page(session, page, per_page)

    print(f"Page={page}, has_previous={result['has_previous']}, has_next={result['has_next']}, total_count={result['total_count']}")

    items = result["items"]
    if not items:
        return "Товары не найдены", None

    product = items[0]

    if product.photo_url:
        content = InputMediaPhoto(
            media=product.photo_url,
            caption=(
                f"<b>✨ {product.name}</b>\n"
                f"<i>СУМКА ИЗ БУСИН</i>\n"
                f"• • • • •"
            ),
            parse_mode="HTML"
        )
    else:
        content = (
            f"<b>✨ {product.name}</b>\n"
            f"<i>СУМКА ИЗ БУСИН</i>\n"
            f"• • • • •"
        )

    keyboard = build_product_keyboard(
        level=level,
        menu_name=menu_name,
        page=page,
        has_previous=result["has_previous"],
        has_next=result["has_next"],
        product_id=product.id,
    )

    return content, keyboard


     
async def get_menu_level_content(session: AsyncSession, level: int, menu_name: str, page: int = 1):
    if level == 0:
        return await menu_level_0(session, level, menu_name)
    elif level == 1:
        return await menu_level_1(session, level, menu_name, page)
   
    
    