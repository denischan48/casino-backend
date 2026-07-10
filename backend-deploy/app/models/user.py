"""
Таблица пользователей.
Одна строка = один игрок, пришедший из Telegram.
"""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    # Внутренний id в нашей базе
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # id пользователя в Telegram (уникальный, по нему находим юзера)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)

    username: Mapped[str | None] = mapped_column(String, nullable=True)
    first_name: Mapped[str | None] = mapped_column(String, nullable=True)

    # Баланс в игровых монетах (GC). На фронте это поле "баланс"
    balance: Mapped[int] = mapped_column(Integer, default=1000)

    # Сколько друзей пригласил
    invites: Mapped[int] = mapped_column(Integer, default=0)

    # Сколько игр сыграл
    games_played: Mapped[int] = mapped_column(Integer, default=0)

    # Самый крупный выигрыш
    top_win: Mapped[int] = mapped_column(Integer, default=0)

    is_vip: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
