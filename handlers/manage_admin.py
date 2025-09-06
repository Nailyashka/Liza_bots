# handlers/manage_admins.py
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.admin_kb import superadmin_main_keyboard
from orm_query.admin import add_admin, get_user_by_username, remove_admin, list_admins, is_superadmin
from states.admin import AddAdminFSM, RemoveAdminFSM

manage_admins_router = Router()


# --- Клавиатуры ---
cancel_kb = types.ReplyKeyboardMarkup(
    keyboard=[[types.KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True,
    one_time_keyboard=True
)


# --- Добавление админа ---
@manage_admins_router.message(F.text == "👑 Добавить админа")
async def start_add_admin(message: types.Message, state: FSMContext, session: AsyncSession):
    if not await is_superadmin(session, message.from_user.id):
        await message.answer("⛔ Нет прав.")
        return

    await message.answer(
        "Введите ID или username пользователя (без @), чтобы назначить его админом:",
        reply_markup=cancel_kb
    )
    await state.set_state(AddAdminFSM.waiting_for_user_input)


@manage_admins_router.message(AddAdminFSM.waiting_for_user_input)
async def process_add_admin(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Добавление админа отменено.", reply_markup=superadmin_main_keyboard())
        return

    input_text = message.text.strip()


    # Попробуем как ID
    if input_text.isdigit():
        tg_id = int(input_text)
        success = await add_admin(session, tg_id)
        if success:
            await message.answer(f"✅ Пользователь {tg_id} теперь админ.", reply_markup=superadmin_main_keyboard())
        else:
            await message.answer("⚠️ Пользователь с таким ID не найден.", reply_markup=superadmin_main_keyboard())
        await state.clear()
        return

    # Если не число — ищем по username
    username = input_text.lstrip("@")
    user = await get_user_by_username(session, username)
    if not user:
        await message.answer("⚠️ Пользователь с таким username не найден.", reply_markup=superadmin_main_keyboard())
        await state.clear()
        return

    success = await add_admin(session, user.tg_id)
    if success:
        await message.answer(f"✅ Пользователь @{username} теперь админ.", reply_markup=superadmin_main_keyboard())
    else:
        await message.answer("⚠️ Ошибка при назначении админа.", reply_markup=superadmin_main_keyboard())
    await state.clear()


# --- Удаление админа ---
@manage_admins_router.message(F.text == "❌ Удалить админа")
async def start_remove_admin(message: types.Message, state: FSMContext, session: AsyncSession):
    if not await is_superadmin(session, message.from_user.id):
        await message.answer("⛔ Нет доступа.")
        return

    await message.answer(
        "Введите ID или username пользователя (без @), чтобы снять права администратора:",
        reply_markup=cancel_kb
    )
    await state.set_state(RemoveAdminFSM.waiting_for_user_id)


@manage_admins_router.message(RemoveAdminFSM.waiting_for_user_id)
async def process_remove_admin(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Удаление админа отменено.", reply_markup=types.ReplyKeyboardRemove())
        return

    input_text = message.text.strip()


    # Попробуем как ID
    if input_text.isdigit():
        tg_id = int(input_text)
        success = await remove_admin(session, tg_id)
        if success:
            await message.answer(f"✅ Пользователь {tg_id} больше не администратор.", reply_markup=superadmin_main_keyboard())
        else:
            await message.answer("❌ Пользователь не найден или он не администратор.", reply_markup=superadmin_main_keyboard())
        await state.clear()
        return

    # Если не число — ищем по username
    username = input_text.lstrip("@")
    user = await get_user_by_username(session, username)
    if not user:
        await message.answer("⚠️ Пользователь с таким username не найден.", reply_markup=superadmin_main_keyboard())
        await state.clear()
        return

    success = await remove_admin(session, user.tg_id)
    if success:
        await message.answer(f"✅ Пользователь @{username} больше не администратор.", reply_markup=superadmin_main_keyboard())
    else:
        await message.answer("❌ Пользователь не найден или он не администратор.", reply_markup=superadmin_main_keyboard())
    await state.clear()


# --- Список админов ---
@manage_admins_router.message(F.text == "📋 Список админов")
async def list_admins_handler(message: types.Message, session: AsyncSession):
    if not await is_superadmin(session, message.from_user.id):
        await message.answer("⛔ Нет доступа.")
        return

    admins = await list_admins(session)
    if not admins:
        await message.answer("📭 Админов пока нет.", reply_markup=superadmin_main_keyboard())
        return

    text = "📋 Список администраторов:\n\n"
    for admin in admins:
        text += f"🆔 {admin.tg_id} | @{admin.username or 'Без ника'} | {admin.full_name}\n"

    await message.answer(text, reply_markup=superadmin_main_keyboard())
