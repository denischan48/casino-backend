"""
Таблица админов — список telegram_id, у кого есть доступ к админ-ручкам
(редактирование кейсов/яиц, создание конкурсов и т.д.).

ПОМЕТКА ДЕНИСУ: чтобы выдать себе доступ, просто добавь строку в эту
таблицу с твоим telegram_id (сделаем это через Neon-консоль или отдельный
скрипт при первом запуске).
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
