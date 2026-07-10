"""
Таблицы яиц (Eggs). Структура один в один как у кейсов (app/models/case.py) —
намеренно, чтобы роуты и сервис открытия можно было переиспользовать.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Egg(Base):
    __tablename__ = "eggs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String)
    image_url: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(Integer)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EggItem(Base):
    __tablename__ = "egg_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    egg_id: Mapped[int] = mapped_column(ForeignKey("eggs.id"), index=True)

    name: Mapped[str] = mapped_column(String)
    image_url: Mapped[str] = mapped_column(String)
    value: Mapped[int] = mapped_column(Integer)
    weight: Mapped[float] = mapped_column(Float)
