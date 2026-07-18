"""
Роут раздела "Апгрейды" — версия с апгрейдом сразу НЕСКОЛЬКИХ предметов.

  GET  /upgrade/inventory                    — что лежит у юзера прямо сейчас
  GET  /upgrade/targets?item_ids=1,2,3        — во что можно апгрейднуть СУММУ выбранных предметов + шансы
  POST /upgrade/attempt                       — попытка апгрейда суммы предметов (честный ролл)

ПОМЕТКА ДЕНИСУ: логика шанса не поменялась (та же формула из upgrade_service.py) —
просто вместо цены одного предмета теперь берём сумму цен всех выбранных.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
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
            continue
        result.append(
            InventoryItemOut(
                id=row.id,
                nft=NftOut(id=nft.id, name=nft.name, image_url=nft.image_url, value=nft.value),
                source=row.source,
                obtained_at=row.obtained_at,
            )
        )
    return result


def _load_owned_items(db: Session, user: User, item_ids: list[int]) -> list[tuple[UserInventory, NftCatalog]]:
    """
    Достаёт из базы все запрошенные предметы инвентаря, проверяя что они
    реально принадлежат юзеру. Бросает 400/404, если что-то не сходится.
    """
    if not item_ids:
        raise HTTPException(status_code=400, detail="Нужно выбрать хотя бы один предмет")

    unique_ids = list(set(item_ids))

    rows = (
        db.query(UserInventory)
        .filter(UserInventory.id.in_(unique_ids), UserInventory.user_id == user.id)
        .all()
    )

    if len(rows) != len(unique_ids):
        raise HTTPException(status_code=404, detail="Один или несколько предметов не найдены в твоём инвентаре")

    result = []
    for row in rows:
        nft = db.query(NftCatalog).filter(NftCatalog.id == row.nft_id).first()
        if not nft:
            raise HTTPException(status_code=404, detail="Предмет отсутствует в каталоге")
        result.append((row, nft))
    return result


@router.get("/targets", response_model=list[UpgradeTargetOut])
def get_targets(
    item_ids: str = Query(..., description="id предметов инвентаря через запятую, например 1,2,3"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        ids = [int(x) for x in item_ids.split(",") if x.strip() != ""]
    except ValueError:
        raise HTTPException(status_code=400, detail="item_ids должен быть списком чисел через запятую")

    owned = _load_owned_items(db, user, ids)
    total_value = sum(nft.value for _, nft in owned)

    candidates = (
        db.query(NftCatalog)
        .filter(NftCatalog.value > total_value)
        .order_by(NftCatalog.value.asc())
        .all()
    )

    return [
        UpgradeTargetOut(
            nft_id=c.id,
            name=c.name,
            image_url=c.image_url,
            value=c.value,
            chance=upgrade_service.calc_chance(total_value, c.value),
        )
        for c in candidates
    ]


@router.post("/attempt", response_model=UpgradeAttemptOut)
def attempt_upgrade(
    payload: UpgradeAttemptIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    owned = _load_owned_items(db, user, payload.inventory_item_ids)
    total_value = sum(nft.value for _, nft in owned)

    target_nft = db.query(NftCatalog).filter(NftCatalog.id == payload.target_nft_id).first()
    if not target_nft:
        raise HTTPException(status_code=404, detail="Целевой предмет отсутствует в каталоге")

    if target_nft.value <= total_value:
        raise HTTPException(status_code=400, detail="Цель должна быть дороже суммы отдаваемых предметов")

    # --- шанс считаем СЕРВЕРОМ заново, от суммы, не доверяя фронту ---
    chance = upgrade_service.calc_chance(total_value, target_nft.value)

    # --- честный ролл ---
    roll_value, used_nonce = fairness_service.next_roll(db, user)
    win = roll_value < chance

    result_item = None
    lost_items = None

    # --- все отданные предметы в любом случае покидают инвентарь (риск) ---
    for inv_item, _nft in owned:
        db.delete(inv_item)

    if win:
        new_item = UserInventory(user_id=user.id, nft_id=target_nft.id, source="upgrade")
        db.add(new_item)
        result_item = UpgradeResultItemOut(
            name=target_nft.name, image_url=target_nft.image_url, value=target_nft.value
        )
    else:
        lost_items = [
            UpgradeResultItemOut(name=nft.name, image_url=nft.image_url, value=nft.value)
            for _inv_item, nft in owned
        ]

    round_row = GameRound(
        user_id=user.id,
        game_type="upgrade",
        bet_amount=total_value,
        payout=target_nft.value if win else 0,
        multiplier=round(target_nft.value / total_value, 4) if win else None,
        is_win=win,
        meta={
            "input_nft_ids": [nft.id for _inv_item, nft in owned],
            "input_total_value": total_value,
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

    # --- всё разом одной транзакцией: либо все удаления + начисление + запись раунда, либо ничего ---
    db.commit()
    db.refresh(user)

    return {
        "win": win,
        "chance": chance,
        "roll": roll_value,
        "result_item": result_item,
        "lost_items": lost_items,
        "nonce": used_nonce,
        "server_seed_hash": user.server_seed_hash,
    }
