"""
Таблица game_rounds — ОДНА история для ВСЕХ игр (мины, дайс, монетка,
открытие кейса, открытие яйца, апгрейд).

ПОМЕТКА ДЕНИСУ: почему одна таблица на все игры, а не отдельная под каждую —
структура ставки у всех игр одинаковая (кто, сколько поставил, что выиграл,
когда). Разница только в деталях самой игры (какие клетки открыл в минах,
какой приз выпал из кейса) — эти детали кладём в поле meta как JSON,
чтобы не плодить кучу похожих таблиц. Эта же таблица потом станет
источником для "живой ленты" на фронте — просто берём последние строки.
"""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class GameRound(Base):
    __tablename__ = "game_rounds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # "mines" | "dice" | "coin" | "case" | "egg" | "upgrade"
    game_type: Mapped[str] = mapped_column(String, index=True)

    bet_amount: Mapped[int] = mapped_column(Integer)

    # Сколько вернулось игроку (0, если проиграл)
    payout: Mapped[int] = mapped_column(Integer, default=0)

    # Множитель выигрыша, например 1.96 — для игр, где он есть (дайс, монетка, мины)
    multiplier: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Победа или нет — удобно для быстрых выборок (лидерборд, статистика)
    is_win: Mapped[bool] = mapped_column(default=False)

    # Детали конкретной игры в свободном виде.
    # Пример для мин: {"mines_count": 5, "opened_cells": [1,4,9]}
    # Пример для кейса: {"case_id": 3, "item_id": 12, "item_name": "AK-47"}
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
