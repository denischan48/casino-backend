"""
Схемы для Provably Fair и игр "Монетка" / "Дайс".
"""

from pydantic import BaseModel


# ---------- Provably Fair ----------

class FairnessOut(BaseModel):
    """То, что игрок видит ДО ставки — публичная часть пары сидов."""
    client_seed: str
    server_seed_hash: str
    nonce: int


class ClientSeedIn(BaseModel):
    """Игрок хочет задать свой client_seed вручную."""
    client_seed: str


class RotateSeedOut(BaseModel):
    """Ответ при смене пары сидов — старый сид раскрывается для проверки."""
    revealed_server_seed: str
    revealed_server_seed_hash: str
    new_server_seed_hash: str


# ---------- Монетка ----------

class CoinBetIn(BaseModel):
    bet_amount: int
    side: str  # "heads" | "tails"


class CoinBetOut(BaseModel):
    win: bool
    side: str
    roll: float
    payout: int
    new_balance: int
    multiplier: float
    nonce: int
    server_seed_hash: str


# ---------- Дайс ----------

class DiceBetIn(BaseModel):
    bet_amount: int
    threshold: float       # порог %, от 2 до 98
    mode: str              # "over" | "under"


class DiceBetOut(BaseModel):
    win: bool
    threshold: float
    mode: str
    roll: float
    payout: int
    new_balance: int
    multiplier: float
    nonce: int
    server_seed_hash: str
