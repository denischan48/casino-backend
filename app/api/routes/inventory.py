"""
Роут продажи NFT обратно казино (buyback 1:1).

  POST /inventory/sell — продать конкретный предмет из своего инвентаря,
                          цена берётся из nft_catalog на сервере (не с фронта).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.nft import NftCatalog, UserInventory
from app.models.user import User
from app.schemas.inventory import InventorySellIn, InventorySellOut
from app.services import balance_service

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.post("/sell", response_model=InventorySellOut)
def sell_item(
    payload: InventorySellIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # --- 1. находим предмет и проверяем, что он принадлежит текущему юзеру ---
    inv_item = (
        db.query(UserInventory)
        .filter(UserInventory.id == payload.inventory_id, UserInventory.user_id == user.id)
        .first()
    )
    if not inv_item:
        raise HTTPException(status_code=404, detail="Предмет не найден в твоём инвентаре")

    # --- 2. цена СТРОГО из каталога на сервере, фронту тут доверять нельзя ---
    nft = db.query(NftCatalog).filter(NftCatalog.id == inv_item.nft_id).first()
    if not nft:
        raise HTTPException(status_code=404, detail="Предмет отсутствует в каталоге")

    price = nft.value

    # --- 3-4. удаляем из инвентаря и начисляем баланс одной операцией ---
    # ПОМЕТКА ДЕНИСУ: db.delete() только помечает запись на удаление в сессии,
    # реального удаления не происходит, пока не случится commit(). А commit()
    # внутри change_balance() сохранит ОБА изменения разом (и удаление предмета,
    # и начисление баланса) — либо оба применятся, либо ни одно (при ошибке
    # выше по коду вообще ничего в базу не попадёт, мы ещё не дошли до commit).
    db.delete(inv_item)
    balance_service.change_balance(db, user, price, f"Продажа NFT: {nft.name}")

    return {
        "sold": True,
        "amount": price,
        "new_balance": user.balance,
    }
