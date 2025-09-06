from aiogram import Router, types
from aiogram.filters import Command

admin_tools_router = Router()

@admin_tools_router.message(Command("get_id"))
async def get_user_id(message: types.Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        await message.answer(f"🆔 ID пользователя: <code>{user.id}</code>", parse_mode="HTML")
    elif message.entities:
        username = message.text.split()[-1].replace("@", "")
        await message.answer(f"🔍 Укажите username через reply или @username.\nПока что reply работает 100%.")
    else:
        await message.answer("⚠️ Ответьте на сообщение пользователя или укажите @username")
