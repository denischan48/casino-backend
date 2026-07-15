"""
Таблицы кейсов.

Case      — сам кейс (витрина, которую ты редактируешь как админ:
            название, цена, картинка, включён/выключен).
CaseItem  — призы внутри конкретного кейса + шанс выпадения каждого.

ПОМЕТКА ДЕНИСУ: раз это лежит в базе, а не захардкожено во фронте —
добавить новый кейс или поменять шансы можно будет через админ-ручку
(напишем её позже), без изменения кода и без пересборки фронта.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String)
    image_url: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(Integer)

    # Можно временно скрыть кейс из списка, не удаляя его насовсем
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Порядок отображения на странице (меньше — выше в списке)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CaseItem(Base):
    __tablename__ = "case_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)

    name: Mapped[str] = mapped_column(String)
    image_url: Mapped[str] = mapped_column(String)

    # Реальная ценность приза в монетах (нужна для расчёта честного шанса/RTP кейса)
    value: Mapped[int] = mapped_column(Integer)

    # Вес шанса выпадения. Не проценты напрямую — берём вес каждого приза
    # и делим на сумму весов всех призов кейса. Так удобнее добавлять новые
    # призы, не пересчитывая вручную проценты у остальных.
    weight: Mapped[float] = mapped_column(Float)
