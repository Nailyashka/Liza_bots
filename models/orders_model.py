from sqlalchemy import String, DateTime, func, Boolean, Integer, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base_model import Base
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from models.users_model import User
    from models.products_model import Product
    
    
    
class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)

    color: Mapped[str] = mapped_column(String(100), nullable=False)      # Цвет сумочки
    lining: Mapped[bool] = mapped_column(Boolean, nullable=False)        # Подкладка Да/Нет
    event: Mapped[str] = mapped_column(String(255), nullable=False)      # Мероприятие
    city: Mapped[str] = mapped_column(String(255), nullable=False)       # Город доставки
    phone: Mapped[str] = mapped_column(String(50), nullable=False)       # Телефон клиента


    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")
