from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.enums_model import UserRole
from models.users_model import User

#TODO Проверка админа при создании БД
async def check_admin(session: AsyncSession, user_id):
    query = await session.execute(select(User).where(User.tg_id == user_id))
    if not query.scalar_one_or_none():
        session.add(User(tg_id=user_id, role = UserRole.superadmin))
    await session.commit()