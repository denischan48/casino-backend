"""
Таблицы конкурсов — под будущую кнопку "добавить ивент" в админке.

Contest             — сам конкурс (создаётся админом вручную).
ContestParticipant  — кто участвует и с каким результатом.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Contest(Base):
    __tablename__ = "contests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    prize: Mapped[str] = mapped_column(String)  # текстом, например "1000 GC"

    start_at: Mapped[datetime] = mapped_column(DateTime)
    end_at: Mapped[datetime] = mapped_column(DateTime)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ContestParticipant(Base):
    __tablename__ = "contest_participants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    contest_id: Mapped[int] = mapped_column(ForeignKey("contests.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # Например накопленный результат для конкурса ("больше всех выиграл")
    score: Mapped[int] = mapped_column(Integer, default=0)

    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
