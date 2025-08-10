# models/product.py
from sqlalchemy import String, Integer, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base_model import Base
from models.orders_model import Order
from typing import TYPE_CHECKING



if TYPE_CHECKING:
    from models.orders_model import Order


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="product")
