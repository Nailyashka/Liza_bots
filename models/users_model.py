# models/user.py
from sqlalchemy import String, Integer, DateTime, func, Enum, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from models.base_model import Base
from models.enums_model import UserRole
from models.orders_model import Order
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from models.orders_model import Order 
 

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(200),default="Без имени", nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.user, nullable=False)
    
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")

