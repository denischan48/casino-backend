"""
Роут игры "Мины".

Три ручки:
  POST /mines/start    — ставим, получаем поле, честно раскладываем мины (секретно)
  POST /mines/open      — открываем клетку: либо мина (проигрыш), либо растёт множитель
  POST /mines/cashout   — забираем текущий накопленный выигрыш, не рискуя дальше

ПОМЕТКА ДЕНИСУ: сам раунд хранится в game_rounds.meta как обычный JSON —
позиции мин там лежат с самого начала (это нужно бэку для проверки открытий),
но во фронт они никогда не уходят, пока раунд не завершится (проигрыш/выигрыш).
Так игрок не может подсмотреть, где мины, через дебаг запросов в браузере.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.bet import GameRound
from app.models.user import User
from app.schemas.mines import (
    MinesCashoutIn,
    MinesCashoutOut,
    MinesOpenIn,
    MinesOpenOut,
    MinesStartIn,
    MinesStartOut,
)
from app.services import balance_service, fairness_service, mines_service

router = APIRouter(prefix="/mines", tags=["mines"])

MIN_BET = 1
MIN_MINES = 1
MAX_MINES = 24


def _get_active_round(db: Session, user: User, round_id: int) -> GameRound:
    round_row = (
        db.query(GameRound)
        .filter(GameRound.id == round_id, GameRound.user_id == user.id, GameRound.game_type == "mines")
        .first()
    )
    if not round_row:
        raise HTTPException(status_code=404, detail="Раунд не найден")
    if round_row.meta.get("status") != "active":
        raise HTTPException(status_code=400, detail="Раунд уже завершён")
    return round_row


@router.post("/start", response_model=MinesStartOut)
def start_round(
    payload: MinesStartIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not (MIN_MINES <= payload.mines_count <= MAX_MINES):
        raise HTTPException(status_code=400, detail=f"mines_count должен быть от {MIN_MINES} до {MAX_MINES}")

    if payload.bet_amount < MIN_BET:
        raise HTTPException(status_code=400, detail=f"Минимальная ставка {MIN_BET}")

    if payload.bet_amount > user.balance:
        raise HTTPException(status_code=400, detail="Недостаточно средств")

    # --- списываем ставку сразу ---
    balance_service.change_balance(db, user, -payload.bet_amount, "Ставка Мины")

    # --- честная раскладка мин ---
    positions, used_nonce = fairness_service.next_shuffle(db, user, n=mines_service.TOTAL_CELLS)
    mine_positions = positions[: payload.mines_count]

    round_row = GameRound(
        user_id=user.id,
        game_type="mines",
        bet_amount=payload.bet_amount,
        payout=0,
        multiplier=None,
        is_win=False,
        meta={
            "status": "active",
            "mines_count": payload.mines_count,
            "mine_positions": mine_positions,
            "opened_cells": [],
            "nonce": used_nonce,
            "server_seed_hash": user.server_seed_hash,
            "client_seed": user.client_seed,
        },
    )
    db.add(round_row)
    db.commit()
    db.refresh(round_row)

    return {
        "round_id": round_row.id,
        "mines_count": payload.mines_count,
        "grid_size": mines_service.TOTAL_CELLS,
        "current_multiplier": 1.0,
        "nonce": used_nonce,
        "server_seed_hash": user.server_seed_hash,
    }


@router.post("/open", response_model=MinesOpenOut)
def open_cell(
    payload: MinesOpenIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    round_row = _get_active_round(db, user, payload.round_id)
    meta = dict(round_row.meta)  # копия, чтобы гарантированно перезаписать поле целиком

    if not (0 <= payload.cell_index < mines_service.TOTAL_CELLS):
        raise HTTPException(status_code=400, detail="cell_index должен быть 0-24")

    if payload.cell_index in meta["opened_cells"]:
        raise HTTPException(status_code=400, detail="Эта клетка уже открыта")

    is_mine = payload.cell_index in meta["mine_positions"]

    if is_mine:
        # --- проигрыш: раскрываем все мины, раунд завершён ---
        meta["status"] = "lost"
        round_row.meta = meta
        round_row.is_win = False
        round_row.payout = 0
        db.commit()

        return {
            "status": "lost",
            "cell_index": payload.cell_index,
            "is_mine": True,
            "opened_cells": meta["opened_cells"],
            "current_multiplier": 0.0,
            "payout": 0,
            "new_balance": user.balance,
            "mine_positions": meta["mine_positions"],
        }

    # --- безопасная клетка ---
    meta["opened_cells"].append(payload.cell_index)
    opened_count = len(meta["opened_cells"])
    current_multiplier = mines_service.calc_multiplier(opened_count, meta["mines_count"])

    max_opens = mines_service.max_safe_opens(meta["mines_count"])
    if opened_count >= max_opens:
        # --- открыл вообще все безопасные клетки — авто-выигрыш по максимуму ---
        payout = round(round_row.bet_amount * current_multiplier)
        meta["status"] = "won"
        round_row.meta = meta
        round_row.is_win = True
        round_row.payout = payout
        round_row.multiplier = current_multiplier
        balance_service.change_balance(db, user, payout, "Выигрыш Мины")
        user.games_played += 1
        if payout > user.top_win:
            user.top_win = payout
        db.commit()
        db.refresh(user)

        return {
            "status": "won",
            "cell_index": payload.cell_index,
            "is_mine": False,
            "opened_cells": meta["opened_cells"],
            "current_multiplier": current_multiplier,
            "payout": payout,
            "new_balance": user.balance,
            "mine_positions": meta["mine_positions"],
        }

    # --- игра продолжается ---
    round_row.meta = meta
    db.commit()

    return {
        "status": "active",
        "cell_index": payload.cell_index,
        "is_mine": False,
        "opened_cells": meta["opened_cells"],
        "current_multiplier": current_multiplier,
        "payout": None,
        "new_balance": None,
        "mine_positions": None,
    }


@router.post("/cashout", response_model=MinesCashoutOut)
def cashout(
    payload: MinesCashoutIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    round_row = _get_active_round(db, user, payload.round_id)
    meta = dict(round_row.meta)

    opened_count = len(meta["opened_cells"])
    if opened_count == 0:
        raise HTTPException(status_code=400, detail="Нужно открыть хотя бы одну клетку перед тем, как забрать выигрыш")

    current_multiplier = mines_service.calc_multiplier(opened_count, meta["mines_count"])
    payout = round(round_row.bet_amount * current_multiplier)

    meta["status"] = "cashed_out"
    round_row.meta = meta
    round_row.is_win = True
    round_row.payout = payout
    round_row.multiplier = current_multiplier

    balance_service.change_balance(db, user, payout, "Выигрыш Мины (забрал)")
    user.games_played += 1
    if payout > user.top_win:
        user.top_win = payout
    db.commit()
    db.refresh(user)

    return {
        "payout": payout,
        "multiplier": current_multiplier,
        "new_balance": user.balance,
        "mine_positions": meta["mine_positions"],
    }
