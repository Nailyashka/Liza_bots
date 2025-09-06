# handlers/superadmin.py
from aiogram import Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession

from aiogram.filters import Command
from keyboards.admin_kb import superadmin_main_keyboard
from orm_query.admin import is_superadmin
from filters.admin_role import IsSuperAdmin

superadmin_router = Router()


@superadmin_router.message(IsSuperAdmin(),Command("superadmin"))
async def superadmin_panel(message: types.Message, session:AsyncSession ):
    await message.answer("👑 Привет, Босс! Что хочешь сделать?", reply_markup=superadmin_main_keyboard())
