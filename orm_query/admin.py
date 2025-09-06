from sqlalchemy import func, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from models.enums_model import UserRole
from models.users_model import User

#TODO Проверка админа при создании БД
async def check_admin(session: AsyncSession, user_id):
    query = await session.execute(select(User).where(User.tg_id == user_id))
    if not query.scalar_one_or_none():
        session.add(User(tg_id=user_id, role = UserRole.superadmin))
    await session.commit()
    
    

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models.products_model import Product

async def add_product(session: AsyncSession, name: str, photo_url: str):
    product = Product(name=name, photo_url=photo_url)
    session.add(product)
    await session.commit()
    return product

async def get_products(session: AsyncSession, page: int = 1, per_page: int = 5):
    """Получаем товары с пагинацией"""
    offset = (page - 1) * per_page
    result = await session.execute(select(Product).offset(offset).limit(per_page))
    items = result.scalars().all()
    
    total_count = await session.scalar(select(Product).count())  # количество товаров
    has_next = page * per_page < total_count
    has_previous = page > 1
    
    return {"items": items, "has_next": has_next, "has_previous": has_previous, "total": total_count}

async def delete_product(session: AsyncSession, product_id: int) -> bool:
    """Удаляем товар по ID"""
    result = await session.execute(delete(Product).where(Product.id == product_id))
    await session.commit()
    return result.rowcount > 0

async def update_product_name(session: AsyncSession, product_id: int, new_name: str) -> bool:
    product = await session.get(Product, product_id)
    if not product:
        return False
    product.name = new_name
    await session.commit()
    return True

async def update_product_description(session: AsyncSession, product_id: int, new_desc: str) -> bool:
    product = await session.get(Product, product_id)
    if not product:
        return False
    product.description = new_desc
    await session.commit()
    return True

# services/admins.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.users_model import User, UserRole


# 🔹 Добавить админа
async def add_admin(session: AsyncSession, tg_id: int) -> bool:
    stmt = select(User).where(User.tg_id == tg_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return False  # Пользователь не найден

    user.role = UserRole.admin
    await session.commit()
    return True


# 🔹 Удалить админа
async def remove_admin(session: AsyncSession, tg_id: int) -> bool:
    stmt = select(User).where(User.tg_id == tg_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or user.role != UserRole.admin:
        return False  # Либо нет, либо он не админ

    user.role = UserRole.user
    await session.commit()
    return True


# 🔹 Получить список админов
async def list_admins(session: AsyncSession) -> list[User]:
    stmt = select(User).where(User.role == UserRole.admin)
    result = await session.execute(stmt)
    return result.scalars().all()


# 🔹 Проверка на суперадмина
async def is_superadmin(session: AsyncSession, tg_id: int) -> bool:
    stmt = select(User).where(User.tg_id == tg_id, User.role == UserRole.superadmin)
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None

async def get_user_by_username(session, username: str):
    stmt = select(User).where(User.username == username)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()




async def get_products(session: AsyncSession, page: int = 1, per_page: int = 5):
    stmt = (
        select(Product)
        .where(Product.is_deleted == False)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await session.execute(stmt)
    products = result.scalars().all()

    count_stmt = select(func.count(Product.id)).where(Product.is_deleted == False)
    total = await session.scalar(count_stmt)

    return {
        "items": products,
        "total": total,
        "has_previous": page > 1,
        "has_next": total > page * per_page,
    }


async def update_product_name(session, product_id: int, new_name: str):
    await session.execute(update(Product).where(Product.id == product_id).values(name=new_name))
    await session.commit()


async def update_product_description(session, product_id: int, new_description: str):
    await session.execute(update(Product).where(Product.id == product_id).values(description=new_description))
    await session.commit()
    
    
async def soft_delete_product(session: AsyncSession, product_id: int) -> bool:
    stmt = (
        update(Product)
        .where(Product.id == product_id)
        .values(is_deleted=True, deleted_at=datetime.utcnow())
    )
    await session.execute(stmt)
    await session.commit()
    return True

# Опционально: если хочешь физически удалять из БД (ОСТОРОЖНО, без отката)
async def delete_product_permanently(session: AsyncSession, product_id: int) -> bool:
    stmt = delete(Product).where(Product.id == product_id)
    await session.execute(stmt)
    await session.commit()
    return True


PAGE_LIMIT = 1  # сколько товаров на странице, можно менять

async def get_products(session: AsyncSession, page: int = 1):
    offset = (page - 1) * PAGE_LIMIT
    query = select(Product).where(Product.is_deleted == False).offset(offset).limit(PAGE_LIMIT)
    result = await session.execute(query)
    items = result.scalars().all()

    # считаем общее количество товаров
    total_query = await session.execute(select(Product).where(Product.is_deleted == False))
    total_items = total_query.scalars().all()
    total_count = len(total_items)

    has_previous = page > 1
    has_next = page * PAGE_LIMIT < total_count

    return {
        "items": items,
        "has_previous": has_previous,
        "has_next": has_next,
        "page": page,
        "total_count": total_count
    }