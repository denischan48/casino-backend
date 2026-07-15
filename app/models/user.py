"""
Таблица пользователей.
Одна строка = один игрок, пришедший из Telegram.
"""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)

    username: Mapped[str | None] = mapped_column(String, nullable=True)
    first_name: Mapped[str | None] = mapped_column(String, nullable=True)

    balance: Mapped[int] = mapped_column(Integer, default=1000)

    # ПОМЕТКА ДЕНИСУ: invites — это ОБЩИЙ счётчик за всё время (для профиля/бонус
    # центра, никогда не уменьшается). invites_balance — это то, что реально можно
    # потратить (баланс приглашений на главном экране и на бонусный кейс за 2 шт).
    invites: Mapped[int] = mapped_column(Integer, default=0)
    invites_balance: Mapped[int] = mapped_column(Integer, default=0)

    # Накопленный реферальный бонус в TON, ожидающий вывода (10% с первого
    # пополнения приглашённого друга). Реальный вывод подключим позже,
    # когда будет готов кошелёк — пока просто копится здесь.
    referral_ton_balance: Mapped[float] = mapped_column(Float, default=0.0)

    games_played: Mapped[int] = mapped_column(Integer, default=0)
    top_win: Mapped[int] = mapped_column(Integer, default=0)
    is_vip: Mapped[bool] = mapped_column(Boolean, default=False)

    # ---------- Provably Fair ----------
    server_seed: Mapped[str | None] = mapped_column(String, nullable=True)
    server_seed_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    client_seed: Mapped[str | None] = mapped_column(String, nullable=True)
    nonce: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
