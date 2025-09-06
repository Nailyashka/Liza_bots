# handlers/admin_products.py
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters import Command
from aiogram.types import InputMediaPhoto

from states.product_state import ProductEdit, ProductForm
from orm_query.admin import (
    add_product, get_products, soft_delete_product,
    update_product_name
)
from keyboards.admin_kb import admin_main_keyboard, product_manage_keyboard, send_product_card

admin_router = Router()

# --- Панель администратора ---
@admin_router.message(Command("admin"))
async def admin_panel(message: types.Message, session: AsyncSession):
    await message.answer(
        "👋 Привет, админ! Вот что ты можешь сделать:",
        reply_markup=admin_main_keyboard()
    )

# --- Добавление товара ---
@admin_router.message(F.text == "➕ Добавить товар")
async def add_product_start(message: types.Message, state: FSMContext):
    await state.set_state(ProductForm.name)
    await message.answer("Введите название товара:")

@admin_router.message(ProductForm.name)
async def add_product_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(ProductForm.photo)
    await message.answer("Отправьте фото товара:")

@admin_router.message(ProductForm.photo, F.photo)
async def add_product_photo(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    photo_url = message.photo[-1].file_id

    await add_product(session=session, name=data["name"], photo_url=photo_url)
    await state.clear()
    await message.delete()

    result = await get_products(session, page=1)
    if not result["items"]:
        await message.answer("📭 Нет товаров.")
        return

    await send_product_card(
        message_or_call=message,
        product=result["items"][0],
        page=result["page"],
        has_prev=result["has_previous"],
        has_next=result["has_next"]
    )

# --- Список товаров ---
@admin_router.message(F.text == "📦 Список товаров")
async def list_products(message: types.Message, session: AsyncSession):
    result = await get_products(session, page=1)
    if not result["items"]:
        await message.answer("Товары не найдены")
        return

    await send_product_card(
        message_or_call=message,
        product=result["items"][0],
        page=result["page"],
        has_prev=result["has_previous"],
        has_next=result["has_next"]
    )

# --- Пагинация ---
@admin_router.callback_query(F.data.startswith("products_page:"))
async def products_page_callback(call: types.CallbackQuery, session: AsyncSession):
    page = int(call.data.split(":")[1])
    result = await get_products(session, page=page)
    if not result["items"]:
        await call.answer("📭 Нет товаров на этой странице", show_alert=True)
        return

    await send_product_card(
        message_or_call=call,
        product=result["items"][0],
        page=result["page"],
        has_prev=result["has_previous"],
        has_next=result["has_next"]
    )
    await call.answer()

# --- Редактирование названия ---
@admin_router.callback_query(F.data.startswith("edit_name:"))
async def start_edit_name(call: types.CallbackQuery, state: FSMContext):
    product_id = int(call.data.split(":")[1])
    await state.update_data(edit_id=product_id)
    await state.set_state(ProductEdit.name)
    await call.message.answer("Введите новое название товара:")

@admin_router.message(ProductEdit.name)
async def edit_product_name(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    product_id = data["edit_id"]

    success = await update_product_name(session, product_id, message.text)
    if not success:
        await message.answer("❌ Ошибка при изменении названия")
        await state.clear()
        return

    result = await get_products(session, page=1)
    product = next((p for p in result["items"] if p.id == product_id), None)
    if not product:
        await message.answer("⚠️ Не удалось найти товар")
        await state.clear()
        return

    await send_product_card(
        message_or_call=message,
        product=product,
        page=result["page"],
        has_prev=result["has_previous"],
        has_next=result["has_next"]
    )
    await message.answer("✅ Название изменено!")
    await state.clear()

# --- Удаление товара ---
@admin_router.callback_query(F.data.startswith("delete:"))
async def delete_product_handler(call: types.CallbackQuery, session: AsyncSession):
    product_id = int(call.data.split(":")[1])
    await soft_delete_product(session, product_id)

    page = 1
    result = await get_products(session, page=page)
    await call.message.delete()
    await call.answer("❌ Товар удалён")

    if not result["items"]:
        await call.message.answer(
            "📭 Товаров больше нет.\nНажмите кнопку ниже, чтобы добавить новый товар.",
            reply_markup=admin_main_keyboard()
        )
    else:
        await send_product_card(
            message_or_call=call,
            product=result["items"][0],
            page=result["page"],
            has_prev=result["has_previous"],
            has_next=result["has_next"]
        )
