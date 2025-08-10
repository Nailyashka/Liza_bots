from aiogram.filters import Filter
from aiogram import types
from sqlalchemy import select

from models.enums_model import UserRole
from models.users_model import User

class IsAdmin(Filter):
    async def __call__(self, message: types.Message, session=None) -> bool:
        if session is None:
            return False
        query = select(User).where(User.tg_id == message.from_user.id, User.role == UserRole.admin)
        result = await session.execute(query)
        return result.scalar_one_or_none() is not None

class IsSuperAdmin(Filter):
    async def __call__(self, message: types.Message, session=None) -> bool:
        if session is None:
            # Если сессии нет — фильтр не может проверить, возвращаем False
            return False
            #В фильтре принимаем параметр session=None.
            # Aiogram сам передаст туда session из data.

        query = select(User).where(User.tg_id == message.from_user.id, User.role == UserRole.superadmin)
        result = await session.execute(query)
        return result.scalar_one_or_none() is not None

class IsAdminOrSuperAdmin(Filter):
    async def __call__(self, message: types.Message, session=None) -> bool:
        is_admin = await IsAdmin().__call__(message, session=session)
        is_superadmin = await IsSuperAdmin().__call__(message, session=session)
        return is_admin or is_superadmin
