import sqlalchemy 
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from models import User, Product, Order
from models.base_model import Base

from orm_query.admin import check_admin


from config import settings_db, admins_bot


DATABASE_URL = settings_db.DATABASE_URL_asyncpg
engine = create_async_engine(DATABASE_URL, echo = True)
session_maker = async_sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)

async def create_db():
    try:
        # Проверка, какие таблицы будут созданы
        print("Таблицы для создания:", Base.metadata.tables.keys())
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("Все таблицы созданы")
            
        # Явное закрытие соединения
        await engine.dispose()
        
        async with session_maker() as session:
            for admin_id in admins_bot.SUPER_ADMINS:
                await check_admin(session, admin_id)
            
    except SQLAlchemyError as e:
        print(f'ОШИБКА ПРИ СОЗДАНИИ ТАБЛИЦ ->>>\n{e}')
        
        
async def delete_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    except SQLAlchemyError as e:
        print(f'ОШИБКА ПРИ УДАЛЕНИИ ТАБЛИЦ!!! ->>>\n {e}')