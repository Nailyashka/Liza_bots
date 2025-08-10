from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import (
    BigInteger, DateTime, String, Integer, Boolean,
    ForeignKey, Text, UniqueConstraint, func
)
from datetime import datetime


class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей.
    Автоматически добавляет поля created и updated с отметками времени.
    """
    created: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
