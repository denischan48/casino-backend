"""
Роут раздела "Апгрейды".

  GET  /upgrade/inventory              — что лежит у юзера прямо сейчас
  GET  /upgrade/targets/{item_id}       — во что можно апгрейднуть конкретный предмет + шансы
  POST /upgrade/attempt                 — попытка апгрейда (честный ролл, риск сгорания предмета)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.bet import GameRound
from app.models.nft import NftCatalog, UserInventory
from app.models.user import User
from app.schemas.game import InventoryItemOut, NftOut
from app.schemas.upgrade import (
    UpgradeAttemptIn,
    UpgradeAttemptOut,
    UpgradeResultItemOut,
    UpgradeTargetOut,
)
from app.services import fairness_service, upgrade_service

router = APIRouter(prefix="/upgrade", tags=["upgrade"])


@router.get("/inventory", response_model=list[InventoryItemOut])
def get_inventory(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = db.query(UserInventory).filter(UserInventory.user_id == user.id).all()
    result = []
    for row in rows:
        nft = db.query(NftCatalog).filter(NftCatalog.id == row.nft_id).first()
        if not nft:
            continue  # на случай если запись каталога когда-то удалили
        result.append(
            InventoryItemOut(
                id=row.id,
                nft=NftOut(id=nft.id, name=nft.name, image_url=nft.image_url, value=nft.value),
                source=row.source,
                obtained_at=row.obtained_at,
            )
        )
    return result


@router.get("/targets/{item_id}", response_model=list[UpgradeTargetOut])
def get_targets(
    item_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    inv_item = (
        db.query(UserInventory)
        .filter(UserInventory.id == item_id, UserInventory.user_id == user.id)
        .first()
    )
    if not inv_item:
        raise HTTPException(status_code=404, detail="Предмет не найден в твоём инвентаре")

    input_nft = db.query(NftCatalog).filter(NftCatalog.id == inv_item.nft_id).first()
    if not input_nft:
        raise HTTPException(status_code=404, detail="Предмет отсутствует в каталоге")

    candidates = (
        db.query(NftCatalog)
        .filter(NftCatalog.value > input_nft.value)
        .order_by(NftCatalog.value.asc())
        .all()
    )

    return [
        UpgradeTargetOut(
            nft_id=c.id,
            name=c.name,
            image_url=c.image_url,
            value=c.value,
            chance=upgrade_service.calc_chance(input_nft.value, c.value),
        )
        for c in candidates
    ]


@router.post("/attempt", response_model=UpgradeAttemptOut)
def attempt_upgrade(
    payload: UpgradeAttemptIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    inv_item = (
        db.query(UserInventory)
        .filter(UserInventory.id == payload.inventory_item_id, UserInventory.user_id == user.id)
        .first()
    )
    if not inv_item:
        raise HTTPException(status_code=404, detail="Предмет не найден в твоём инвентаре")

    input_nft = db.query(NftCatalog).filter(NftCatalog.id == inv_item.nft_id).first()
    target_nft = db.query(NftCatalog).filter(NftCatalog.id == payload.target_nft_id).first()
    if not input_nft or not target_nft:
        raise HTTPException(status_code=404, detail="Предмет отсутствует в каталоге")

    # --- шанс считаем СЕРВЕРОМ заново, не доверяя тому, что было показано раньше ---
    chance = upgrade_service.calc_chance(input_nft.value, target_nft.value)

    # --- честный ролл ---
    roll_value, used_nonce = fairness_service.next_roll(db, user)
    win = roll_value < chance

    result_item = None
    lost_item = None

    # --- исходный предмет в любом случае покидает инвентарь (риск) ---
    db.delete(inv_item)

    if win:
        new_item = UserInventory(user_id=user.id, nft_id=target_nft.id, source="upgrade")
        db.add(new_item)
        result_item = UpgradeResultItemOut(
            name=target_nft.name, image_url=target_nft.image_url, value=target_nft.value
        )
    else:
        lost_item = UpgradeResultItemOut(
            name=input_nft.name, image_url=input_nft.image_url, value=input_nft.value
        )

    round_row = GameRound(
        user_id=user.id,
        game_type="upgrade",
        bet_amount=input_nft.value,
        payout=target_nft.value if win else 0,
        multiplier=round(target_nft.value / input_nft.value, 4) if win else None,
        is_win=win,
        meta={
            "input_nft_id": input_nft.id,
            "input_nft_name": input_nft.name,
            "target_nft_id": target_nft.id,
            "target_nft_name": target_nft.name,
            "chance": chance,
            "roll": roll_value,
            "nonce": used_nonce,
            "server_seed_hash": user.server_seed_hash,
            "client_seed": user.client_seed,
        },
    )
    db.add(round_row)

    user.games_played += 1
    if win and target_nft.value > user.top_win:
        user.top_win = target_nft.value

    db.commit()
    db.refresh(user)

    return {
        "win": win,
        "chance": chance,
        "roll": roll_value,
        "result_item": result_item,
        "lost_item": lost_item,
        "nonce": used_nonce,
        "server_seed_hash": user.server_seed_hash,
    }
