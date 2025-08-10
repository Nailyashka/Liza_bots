from sqlalchemy import func, select
import math
from sqlalchemy.ext.asyncio import AsyncSession

from models.products_model import Product

class UniversalPaginator:
    def __init__(self, page: int = 1, per_page: int = 5):
        self.page = page
        self.per_page = per_page

    def _calc_offsets(self):
        offset = (self.page - 1) * self.per_page
        return offset, self.per_page #todo этот кортеж

    # async def paginate_query(self, session: AsyncSession, base_query):
    #     # todo распковываем кортеж
    #     offset, limit = self._calc_offsets()
    #     # Считаем общее количество (нужно для кнопок "Дальше/Назад")
    #     #* base_query = к примеру: base_query = select(Car).where(Car.city_id == 1) просто какой-то запрос

    #     total_query = base_query.with_only_columns(func.count()).order_by(None)
    #     total_result = await session.execute(total_query)
    #     total_count = total_result.scalar()

    #     # Получаем элементы с LIMIT+OFFSET
    #     query = base_query.offset(offset).limit(limit)
    #     result = await session.execute(query)
    #     items = result.scalars().all()

    #     total_pages = math.ceil(total_count / self.per_page) if total_count else 1

    #     return {
    #         "items": items,
    #         "total_count": total_count,
    #         "total_pages": total_pages,
    #         "current_page": self.page,
    #         "has_next": self.page < total_pages,
    #         "has_previous": self.page > 1,
    #     }
    async def paginate_query(self, session: AsyncSession, base_query):
        offset, limit = self._calc_offsets()

        # Новый способ подсчёта, чтобы всегда считать правильно
        count_query = select(func.count()).select_from(Product)
        total_result = await session.execute(count_query)
        total_count = total_result.scalar()

        query = base_query.offset(offset).limit(limit)
        result = await session.execute(query)
        items = result.scalars().all()

        total_pages = math.ceil(total_count / self.per_page) if total_count else 1

        return {
            "items": items,
            "total_count": total_count,
            "total_pages": total_pages,
            "current_page": self.page,
            "has_next": self.page < total_pages,
            "has_previous": self.page > 1,
        }


    def paginate_list(self, items_list: list):
        offset, limit = self._calc_offsets()
        total_count = len(items_list)
        sliced = items_list[offset:offset + limit]

        total_pages = math.ceil(total_count / self.per_page) if total_count else 1

        return {
            "items": sliced,
            "total_count": total_count,
            "total_pages": total_pages,
            "current_page": self.page,
            "has_next": self.page < total_pages,
            "has_previous": self.page > 1,
        }
        
async def pages(result_dict: dict):
    btns = dict()

    if result_dict["has_previous"]:
        btns['⬅️ Пред.'] = 'previous'

    if result_dict["has_next"]:
        btns['След. ➡️'] = 'next'

    return btns

# btns = await pages(result)
