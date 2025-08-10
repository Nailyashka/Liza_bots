import os
import logging
from venv import logger
from aiogram.types import Message, CallbackQuery
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram import Router
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import F
from aiogram.exceptions import TelegramMigrateToChat
from dotenv import load_dotenv

from sqlalchemy.exc import SQLAlchemyError

from handlers.menu_processing import get_menu_level_content
from keyboards.inline import MenuCallBack
from models.users_model import User
from states.order_state import OrderForm

user_menu = Router()
    
    
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
        await state.set_state(OrderForm.color)  # Запускаем FSM с шага выбора цвета
        await callback.message.answer("Введите желаемый цвет 🖌")
        await callback.answer()
        return  # Завершаем выполнение обработчика, чтобы не шла дальше логика меню

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




@user_menu.message(F.photo)
async def photo_test(message:Message):
    await message.answer(message.photo[-1].file_id)


from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from sqlalchemy import select
from models.users_model import User
from states.order_state import OrderForm


# Шаг 1: ввод цвета (обычный текст)
@user_menu.message(OrderForm.color)
async def process_color(message: types.Message, state: FSMContext):
    await state.update_data(color=message.text)

    # Reply-кнопки "Да"/"Нет" для выбора прокладки
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await state.set_state(OrderForm.lining)
    await message.answer("Желаете выбрать прокладку?", reply_markup=keyboard)


# Шаг 2: ответ "Да" или "Нет" — ввод прокладки или пропуск
# @user_menu.message(OrderForm.lining)
# async def process_lining(message: types.Message, state: FSMContext):
#     if message.text == "Да":
#         # Пользователь хочет ввести подкладку, меняем состояние на ввод текста прокладки
#         await state.set_state(OrderForm.lining_text)
#         await message.answer("Введите желаемый подклад ✂", reply_markup=ReplyKeyboardRemove())
#     elif message.text == "Нет":
#         # Пользователь пропускает подкладку, сохраняем пустое значение и переходим к комментарию
#         await state.update_data(lining="(не выбрано)")
#         await state.set_state(OrderForm.comment)
#         await message.answer("Введите комментарий 📝", reply_markup=ReplyKeyboardRemove())
#     else:
#         # Некорректный ответ — просим ответить "Да" или "Нет"
#         await message.answer('Пожалуйста, выберите "Да" или "Нет" кнопками ниже.')


# Шаг 2.1: ввод текста прокладки (если выбрали "Да")
@user_menu.message(OrderForm.lining)
async def process_lining_text(message: types.Message, state: FSMContext):
    await state.update_data(lining=message.text)
    await state.set_state(OrderForm.comment)
    await message.answer("Введите для какого мероприятия 📝")


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
    if message.contact:
        # Пользователь поделился контактом (если хотите обрабатывать)
        # Тут можно, например, сразу переходить к следующему шагу
        await state.update_data(contact=message.contact.phone_number)
        await state.set_state(OrderForm.final)
        await message.answer("Спасибо, контакт получен. Подтверждаем заказ.", reply_markup=ReplyKeyboardRemove())
        # Можно здесь вызвать функцию отправки заказа
    else:
        # Пользователь ввел город текстом
        await state.update_data(city=message.text)
        # Теперь спросим контакт с кнопкой "Поделиться контактом"
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Поделиться контактом", request_contact=True)]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await state.set_state(OrderForm.contact)
        await message.answer("Введите ваш номер телефона 📞 или нажмите кнопку ниже, чтобы поделиться контактом", reply_markup=keyboard)


# Шаг 5: ввод номера телефона или нажатие кнопки "Поделиться контактом"
@user_menu.message(OrderForm.contact)
async def process_contact(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text

    await state.update_data(contact=phone)

    data = await state.get_data()

    client_message = (
        f"✅ Ваш заказ принят!\n"
        f"Мы свяжемся с вами в ближайшее время.\n\n"
        f"Если захотите что-то изменить — просто напишите нам."
    )
    admin_message = (
        f"🆕 Новый заказ!\n"
        f"Товар: Тут товар\n"
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
