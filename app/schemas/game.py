"""
Схемы для всего игрового блока: ставки, кейсы, яйца, апгрейды, рефералка.
"""

from datetime import datetime

from pydantic import BaseModel


# ---------- Общее для всех игр ----------

class BetIn(BaseModel):
    """То, что фронт присылает, когда делает ставку (дайс/монетка/мины)."""
    bet_amount: int


class GameRoundOut(BaseModel):
    """Результат раунда — универсальный ответ для любой игры."""
    id: int
    game_type: str
    bet_amount: int
    payout: int
    multiplier: float | None
    is_win: bool
    meta: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------- Кейсы ----------

class CaseItemOut(BaseModel):
    """
    Приз внутри кейса, каким его видит фронт.
    ПОМЕТКА ДЕНИСУ: специально нет поля weight/шанс — не отдаём наружу,
    чтобы нельзя было подсмотреть точные шансы через devtools браузера.
    """
    id: int
    name: str
    image_url: str
    value: int

    model_config = {"from_attributes": True}


class CaseOut(BaseModel):
    id: int
    name: str
    image_url: str
    price: int
    items: list[CaseItemOut]

    model_config = {"from_attributes": True}


class CaseOpenResult(BaseModel):
    """Ответ после открытия кейса — что выпало + новый баланс."""
    won_item: CaseItemOut
    new_balance: int


# ---------- Яйца (структура зеркалит кейсы) ----------

class EggItemOut(BaseModel):
    id: int
    name: str
    image_url: str
    value: int

    model_config = {"from_attributes": True}


class EggOut(BaseModel):
    id: int
    name: str
    image_url: str
    price: int
    items: list[EggItemOut]

    model_config = {"from_attributes": True}


class EggOpenResult(BaseModel):
    won_item: EggItemOut
    new_balance: int


# ---------- Апгрейды / инвентарь ----------

class NftOut(BaseModel):
    id: int
    name: str
    image_url: str
    value: int

    model_config = {"from_attributes": True}


class InventoryItemOut(BaseModel):
    id: int
    nft: NftOut
    source: str
    obtained_at: datetime

    model_config = {"from_attributes": True}


# ---------- Рефералка ----------

class ReferralOut(BaseModel):
    invited_id: int
    bonus_paid: bool
    created_at: datetime

    model_config = {"from_attributes": True}
