from sqlalchemy import select
from models.products_model import Product
from orm_query.paginator import UniversalPaginator
from sqlalchemy.ext.asyncio import AsyncSession



async def get_products_page(session: AsyncSession, page: int, per_page: int = 1):
    base_query = select(Product).order_by(Product.id)
    paginator = UniversalPaginator(page=page, per_page=per_page)
    result = await paginator.paginate_query(session, base_query)
    return result
