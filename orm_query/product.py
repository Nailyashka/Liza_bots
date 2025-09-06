import logging
from sqlalchemy import func, select
from models.products_model import Product
from orm_query.paginator import UniversalPaginator
from sqlalchemy.ext.asyncio import AsyncSession



async def get_products_page(session: AsyncSession, page: int = 1, per_page: int = 1):
    base = select(Product).where(Product.is_deleted == False).order_by(Product.id)
    # total:
    total_q = select(func.count()).select_from(Product).where(Product.is_deleted == False)
    total_res = await session.execute(total_q)
    total_count = total_res.scalar_one()
    offset = (page - 1) * per_page

    res = await session.execute(base.limit(per_page).offset(offset))
    items = res.scalars().all()

    return {
        "items": items,
        "has_previous": page > 1,
        "has_next": (offset + per_page) < total_count,
        "total_count": total_count
    }

async def find_product(session: AsyncSession, product_id: int):
    logging.info(f"Тип product_id: {type(product_id)}")

    logging.info(f"[DEBUG] Ищу продукт с id={product_id}")
    query = select(Product).where(Product.id == product_id)
    result = await session.execute(query)
    product = result.scalar_one_or_none()
    logging.info(f"[DEBUG] Найден продукт: {product}")
    return product

