"""
Роут игры "Монетка" (CoinFlip).

Логика: игрок ставит на "орёл" или "решку". Честный результат (0.00-99.99)
считается через Provably Fair (см. app/services/fairness_service.py).
roll < 50 — орёл (heads), roll >= 50 — решка (tails).

Множитель фиксированный x1.96 (50% шанс минус 2% на казино) — чтобы игра
была математически честной в среднем, но у казино было небольшое преимущество.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.bet import GameRound
from app.models.user import User
from app.schemas.fairness import CoinBetIn, CoinBetOut
from app.services import balance_service, fairness_service

router = APIRouter(prefix="/coin", tags=["coin"])

MULTIPLIER = 1.96
MIN_BET = 1


@router.post("/bet", response_model=CoinBetOut)
def place_bet(
    payload: CoinBetIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # --- проверки входных данных ---
    if payload.side not in ("heads", "tails"):
        raise HTTPException(status_code=400, detail="side должен быть 'heads' или 'tails'")

    if payload.bet_amount < MIN_BET:
        raise HTTPException(status_code=400, detail=f"Минимальная ставка {MIN_BET}")

    if payload.bet_amount > user.balance:
        raise HTTPException(status_code=400, detail="Недостаточно средств")

    # --- списываем ставку СРАЗУ, до расчёта исхода ---
    balance_service.change_balance(db, user, -payload.bet_amount, "Ставка Монетка")

    # --- честный бросок ---
    roll_value, used_nonce = fairness_service.next_roll(db, user)
    outcome_side = "heads" if roll_value < 50 else "tails"
    win = outcome_side == payload.side

    payout = 0
    if win:
        payout = round(payload.bet_amount * MULTIPLIER)
        balance_service.change_balance(db, user, payout, "Выигрыш Монетка")

    # --- статистика игрока ---
    user.games_played += 1
    if payout > user.top_win:
        user.top_win = payout
    db.commit()

    # --- запись раунда в общую историю игр ---
    round_row = GameRound(
        user_id=user.id,
        game_type="coin",
        bet_amount=payload.bet_amount,
        payout=payout,
        multiplier=MULTIPLIER if win else None,
        is_win=win,
        meta={
            "side_chosen": payload.side,
            "side_result": outcome_side,
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
        "side": outcome_side,
        "roll": roll_value,
        "payout": payout,
        "new_balance": user.balance,
        "multiplier": MULTIPLIER,
        "nonce": used_nonce,
        "server_seed_hash": user.server_seed_hash,
    }
