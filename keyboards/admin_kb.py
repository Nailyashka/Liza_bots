from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from aiogram import types
from aiogram.types import CallbackQuery



def admin_main_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.add(
        KeyboardButton(text="➕ Добавить товар"),
        KeyboardButton(text="📦 Список товаров")
    )

    return kb.adjust(2,).as_markup(resize_keyboard=True, input_field_placeholder="Выберите действие:")
# У меня уже есть опыт выполнения коммерческих заказов: асинхронное программирование, архитектурные подходы, ORM.
# Для меня важно не просто писать код, а создавать масштабируемые решения. Учёба в Лицее — это логичный шаг,
# чтобы систематизировать знания и работать над реальными проектами.»

def superadmin_main_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.add(
        KeyboardButton(text="👑 Добавить админа"),
        KeyboardButton(text="❌ Удалить админа"),
        KeyboardButton(text="📋 Список админов")
    )
    kb.add(
        KeyboardButton(text="➕ Добавить товар"),
    )

    return kb.adjust(3, 3,).as_markup(resize_keyboard=True, input_field_placeholder="Привет, Босс 👑")

def product_manage_keyboard(product_id: int, page: int):
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete:{product_id}")
    )
    return kb.as_markup()

def products_pagination_keyboard(page: int, has_prev: bool, has_next: bool):
    kb = InlineKeyboardBuilder()
    nav_buttons = []
    if has_prev:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"products_page:{page-1}"))
    if has_next:
        nav_buttons.append(InlineKeyboardButton(text="Листай каталог ➡️", callback_data=f"products_page:{page+1}"))
    if nav_buttons:
        kb.row(*nav_buttons)
    return kb.as_markup()



from aiogram.exceptions import TelegramBadRequest

async def send_product_card(message_or_call, product, page: int, has_prev: bool = False, has_next: bool = False):
    from aiogram.types import InputMediaPhoto, InlineKeyboardButton
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    text = f"<b>✨ {product.name}</b>\n<i>СУМКА ИЗ БУСИН</i>\n• • • • •"

    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="✏️ Изменить название", callback_data=f"edit_name:{product.id}"))
    kb.row(InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete:{product.id}"))

    nav = []
    if has_prev:
        nav.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"products_page:{page-1}"))
    if has_next:
        nav.append(InlineKeyboardButton(text="Листай каталог ➡️", callback_data=f"products_page:{page+1}"))
    if nav:
        kb.row(*nav)

    markup = kb.as_markup()

    try:
        if isinstance(message_or_call, types.CallbackQuery):
            await message_or_call.message.edit_media(
                media=InputMediaPhoto(media=product.photo_url, caption=text, parse_mode="HTML"),
                reply_markup=markup
            )
        else:
            await message_or_call.answer_photo(
                product.photo_url,
                caption=text,
                reply_markup=markup,
                parse_mode="HTML"
            )
    except TelegramBadRequest as e:
        # Если не удалось редактировать — отправляем новое сообщение
        await message_or_call.message.answer_photo(
            product.photo_url,
            caption=text,
            reply_markup=markup,
            parse_mode="HTML"
        )
