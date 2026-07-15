"""
Таблица транзакций — история операций с балансом.
На фронте это блок "ПОСЛЕДНИЕ ТРАНЗАКЦИИ" в кошельке (интерфейс HistoryItem).
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # К какому пользователю относится операция
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # Описание, например "Пополнение TON" или "Ставка Орёл/Решка"
    title: Mapped[str] = mapped_column(String)

    # Сумма в монетах. Плюс — пополнение, минус — трата
    amount: Mapped[int] = mapped_column(Integer)

    # "in" (приход) или "out" (расход) — как на фронте
    direction: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
