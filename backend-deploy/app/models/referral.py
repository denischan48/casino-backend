"""
Таблица рефералов.

Один ряд = один факт "юзер А пригласил юзера Б".
Считаем invites у пользователя не руками (+1 к полю), а количеством строк
в этой таблице — так число нельзя случайно накрутить в обход.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    inviter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # unique=True — один и тот же юзер не может быть "приглашён" дважды
    invited_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)

    # Начислен ли бонус пригласившему за этого друга
    bonus_paid: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
