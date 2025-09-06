from datetime import datetime
from sqlalchemy import Boolean, String, Integer, DateTime, func, Text
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
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="product")
