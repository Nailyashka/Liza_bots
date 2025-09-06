import os
import logging
from venv import logger
from dotenv import load_dotenv

from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramMigrateToChat
from aiogram.fsm.context import FSMContext

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from models.users_model import User
from orm_query.orders import create_order
from orm_query.product import find_product
from orm_query.user import find_user_by_id
from states.order_state import OrderForm
from handlers.menu_processing import get_menu_level_content
from keyboards.inline import MenuCallBack
from keyboards.reply_kb import keyboard_yes_no, keyboard_phone
from utils.check_function import validate_city, validate_phone


user_menu = Router()
    

@user_menu.message(F.text == "т")
async def test_product(message: Message, session: AsyncSession):
    product = await find_product(session, 1)  # поставь реальный ID из базы
    await message.answer(f"Продукт: {product.name if product else 'Не найден'}")

@user_menu.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    content, reply_markup = await get_menu_level_content(session, level=0, menu_name='main')
    
    # проверяем, что пришло — текст или InputMediaPhoto
    if isinstance(content, str):
        await message.answer(text=content,parse_mode='HTML', reply_markup=reply_markup)
    else:
        await message.answer_photo(photo=content.media, caption=content.caption, reply_markup=reply_markup)

@user_menu.callback_query(MenuCallBack.filter())
async def menu_callback_handler(
    callback: CallbackQuery,
    callback_data: MenuCallBack,
    state: FSMContext,
    session: AsyncSession
):
    logging.info(f"Callback received: level={callback_data.level}, page={callback_data.page}")
    print(f"Callback data: level={callback_data.level}, page={callback_data.page}, menu_name={callback_data.menu_name}")

    # Если level == 5 → запускаем FSM
    if callback_data.level == 5:
        await state.clear()
        # Сохраняем product_id в FSM
        await state.update_data(product_id=callback_data.product_id)
        await state.set_state(OrderForm.color)  # Запускаем FSM с шага выбора цвета
        await callback.message.answer("Введите желаемый цвет 🖌")
        await callback.answer()
        return

    # Для остальных уровней — логика меню
    content, markup = await get_menu_level_content(
        session=session,
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        page=callback_data.page
    )
    print("Returned from get_menu_level_content")

    if isinstance(content, str):
        await callback.message.edit_text(content, reply_markup=markup, parse_mode='HTML')
    else:
        await callback.message.edit_media(media=content, reply_markup=markup)

    await callback.answer()

# @user_menu.message(F.photo)
# async def photo_test(message:Message):
#     await message.answer(message.photo[-1].file_id)

# Шаг 1: ввод цвета (обычный текст)
@user_menu.message(OrderForm.color)
async def process_color(message: types.Message, state: FSMContext):
    await state.update_data(color=message.text)

    await state.set_state(OrderForm.lining)
    await message.answer("Желаете выбрать подкладку?", reply_markup=keyboard_yes_no)



# Шаг 2.1: ввод текста прокладки (если выбрали "Да")
@user_menu.message(OrderForm.lining)
async def process_lining_text(message: types.Message, state: FSMContext):
    await state.update_data(lining=message.text)
    await state.set_state(OrderForm.comment)
    await message.answer("Введите для какого мероприятия 📝", reply_markup=ReplyKeyboardRemove())


# Шаг 3: ввод комментария (обычный текст)
@user_menu.message(OrderForm.comment)
async def process_comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)

    # Reply кнопки для выбора города (здесь пример: можно заменить на любой вопрос)
    
    
    await state.set_state(OrderForm.city)
    await message.answer("Введите ваш город 🏙")


# Шаг 4: ввод города или нажатие кнопки "Поделиться контактом"
@user_menu.message(OrderForm.city)
async def process_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    # Теперь спросим контакт с кнопкой "Поделиться контактом"
    await state.set_state(OrderForm.contact)
    await message.answer("Введите ваш номер телефона 📞 или нажмите кнопку ниже, чтобы поделиться контактом", reply_markup=keyboard_phone)


# Шаг 5: ввод номера телефона или нажатие кнопки "Поделиться контактом"
@user_menu.message(OrderForm.contact)
async def process_contact(message: types.Message, state: FSMContext, session: AsyncSession):
    tg_id = message.from_user.id
    
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text

    if not validate_phone(phone):
        await message.answer("❌ Введите корректный номер телефона (+79998887766)")
        return

    data = await state.get_data()

    if not validate_city(data.get("city", "")):
        await message.answer("❌ Введите корректный город")
        return

    await state.update_data(contact=phone)
    data = await state.get_data()
    user = await find_user_by_id(session, tg_id)

    # ✅ Берём product_id из FSM
    product_id = data.get("product_id")
    product = await find_product(session,product_id)

    order = await create_order(
        session=session,
        user_id=user.id,
        product_id=product_id,  # теперь динамический ID
        color=data["color"],
        lining=data["lining"].lower() == "да",
        event=data["comment"],
        city=data["city"],
        phone=data["contact"]
    )

    data = await state.get_data()

    client_message = (
        f"✅ Ваш заказ принят!\n"
        f"Мы свяжемся с вами в ближайшее время.\n\n"
        f"Если захотите что-то изменить — просто напишите нам."
    )
    # 📦 Сообщение админу с названием товара
    admin_message = (
        f"🆕 Новый заказ!\n"
        f"Товар: {product.name if product else 'Не найден'}\n"
        f"Цвет: {data.get('color')}\n"
        f"Подклад: {data.get('lining')}\n"
        f"Комментарий: {data.get('comment')}\n"
        f"Город: {data.get('city')}\n"
        f"Телефон: {data.get('contact')}\n"
        f"Пользователь: @{message.from_user.username or message.from_user.full_name}"
    )


    # Отправляем клиенту
    await message.answer(client_message, reply_markup=ReplyKeyboardRemove())
    await state.clear()

    # Получаем суперадминов
    result = await session.execute(
        select(User).where(User.role == "superadmin")
    )
    admins_list = result.scalars().all()

    for admin in admins_list:
        await message.bot.send_message(admin.tg_id, admin_message, parse_mode="HTML")

    await message.answer("✅ Заказ отправлен! Мы скоро свяжемся с вами.", reply_markup=ReplyKeyboardRemove())
