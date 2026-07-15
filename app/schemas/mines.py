"""
Схемы для игры "Мины".

Игра сессионная (не одна ставка = один ответ, как в монетке/дайсе) —
сначала стартуем раунд, потом по одной открываем клетки, в конце либо
попадаем на мину (проигрыш), либо сами забираем накопленный выигрыш.
"""

from pydantic import BaseModel


class MinesStartIn(BaseModel):
    bet_amount: int
    mines_count: int  # сколько мин на поле, 1-24


class MinesStartOut(BaseModel):
    round_id: int
    mines_count: int
    grid_size: int
    current_multiplier: float
    nonce: int
    server_seed_hash: str


class MinesOpenIn(BaseModel):
    round_id: int
    cell_index: int  # 0-24


class MinesOpenOut(BaseModel):
    status: str  # "active" | "lost" | "won"
    cell_index: int
    is_mine: bool
    opened_cells: list[int]
    current_multiplier: float
    payout: int | None = None       # заполняется только если раунд завершился
    new_balance: int | None = None
    mine_positions: list[int] | None = None  # раскрываются только на проигрыше/финале


class MinesCashoutIn(BaseModel):
    round_id: int


class MinesCashoutOut(BaseModel):
    payout: int
    multiplier: float
    new_balance: int
    mine_positions: list[int]
