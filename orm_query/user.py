from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.enums_model import UserRole
from models.users_model import User

async def find_user_by_id(session: AsyncSession, tg_id: int):
    query = select(User).where(User.tg_id == tg_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()
    