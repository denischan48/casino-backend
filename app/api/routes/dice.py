"""
Роут игры "Дайс".

Логика зеркалит то, что было на фронте в Dice.tsx (Блок до переноса на бэк):
  - Игрок выбирает порог (threshold, 2-98%) и режим НИЖЕ/ВЫШЕ
  - Честный roll — число 0.00-99.99 (Provably Fair)
  - Множитель считается СЕРВЕРОМ по формуле (100 / шанс) * house_edge —
    клиенту нельзя доверять множитель, иначе можно подделать выигрыш

ПОМЕТКА ДЕНИСУ: house edge и границы порога — те же цифры, что были у тебя
на фронте (HOUSE_EDGE=0.99, MIN_PCT=2, MAX_PCT=98), чтобы поведение игры
не поменялось для игрока при переключении на реальный бэк.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.bet import GameRound
from app.models.user import User
from app.schemas.fairness import DiceBetIn, DiceBetOut
from app.services import balance_service, fairness_service

router = APIRouter(prefix="/dice", tags=["dice"])

HOUSE_EDGE = 0.99
MIN_PCT = 2.0
MAX_PCT = 98.0
MIN_BET = 1


def _win_chance(threshold: float, mode: str) -> float:
    """Шанс выигрыша (%) при данном пороге и режиме."""
    return threshold if mode == "under" else 100 - threshold


def _multiplier(threshold: float, mode: str) -> float:
    chance = _win_chance(threshold, mode)
    if chance <= 0:
        return 0.0
    return (100 / chance) * HOUSE_EDGE


@router.post("/bet", response_model=DiceBetOut)
def place_bet(
    payload: DiceBetIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # --- проверки входных данных ---
    if payload.mode not in ("over", "under"):
        raise HTTPException(status_code=400, detail="mode должен быть 'over' или 'under'")

    if not (MIN_PCT <= payload.threshold <= MAX_PCT):
        raise HTTPException(status_code=400, detail=f"threshold должен быть от {MIN_PCT} до {MAX_PCT}")

    if payload.bet_amount < MIN_BET:
        raise HTTPException(status_code=400, detail=f"Минимальная ставка {MIN_BET}")

    if payload.bet_amount > user.balance:
        raise HTTPException(status_code=400, detail="Недостаточно средств")

    # --- списываем ставку СРАЗУ, до расчёта исхода ---
    balance_service.change_balance(db, user, -payload.bet_amount, "Ставка Дайс")

    # --- честный бросок ---
    roll_value, used_nonce = fairness_service.next_roll(db, user)

    win = roll_value < payload.threshold if payload.mode == "under" else roll_value > payload.threshold
    mult = _multiplier(payload.threshold, payload.mode)

    payout = 0
    if win:
        payout = round(payload.bet_amount * mult)
        balance_service.change_balance(db, user, payout, "Выигрыш Дайс")

    # --- статистика игрока ---
    user.games_played += 1
    if payout > user.top_win:
        user.top_win = payout
    db.commit()

    # --- запись раунда в общую историю игр ---
    round_row = GameRound(
        user_id=user.id,
        game_type="dice",
        bet_amount=payload.bet_amount,
        payout=payout,
        multiplier=mult if win else None,
        is_win=win,
        meta={
            "threshold": payload.threshold,
            "mode": payload.mode,
            "roll": roll_value,
            "nonce": used_nonce,
            "server_seed_hash": user.server_seed_hash,
            "client_seed": user.client_seed,
        },
    )
    db.add(round_row)
    db.commit()
    db.refresh(user)

    return {
        "win": win,
        "threshold": payload.threshold,
        "mode": payload.mode,
        "roll": roll_value,
        "payout": payout,
        "new_balance": user.balance,
        "multiplier": mult,
        "nonce": used_nonce,
        "server_seed_hash": user.server_seed_hash,
    }
