"""
Схемы для кошелька и лидерборда.
"""

from pydantic import BaseModel


class HistoryItemOut(BaseModel):
    """Одна строка истории транзакций (как HistoryItem на фронте)."""
    id: int
    title: str
    amount: str        # уже отформатированная строка, например "+2,875"
    date: str
    type: str          # "in" или "out"


class WalletOut(BaseModel):
    """Полный ответ для страницы Кошелёк."""
    balance: int
    history: list[HistoryItemOut]


class LeaderOut(BaseModel):
    """Один игрок в таблице лидеров (как Leader на фронте)."""
    id: int
    rank: int
    username: str
    avatar: str
    winAmount: str
    isVIP: bool
