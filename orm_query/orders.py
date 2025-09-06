# services/orders.py
from sqlalchemy.ext.asyncio import AsyncSession
from models.orders_model import Order

async def create_order(
    session: AsyncSession,
    user_id: int,
    product_id: int,
    color: str,
    lining: bool,
    event: str,
    city: str,
    phone: str
) -> Order:
    """Создаёт заказ и сохраняет в БД."""
    new_order = Order(
        user_id=user_id,
        product_id=product_id,
        color=color,
        lining=lining,
        event=event,
        city=city,
        phone=phone
    )
    session.add(new_order)
    await session.commit()
    await session.refresh(new_order)
    return new_order
