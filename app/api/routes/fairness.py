"""
Роут честности игры. Общий для ВСЕХ игр (монетка, дайс, мины) —
пара сидов у игрока одна на все игры, просто nonce общий счётчик.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.fairness import ClientSeedIn, FairnessOut, RotateSeedOut
from app.services import fairness_service

router = APIRouter(prefix="/fairness", tags=["fairness"])


@router.get("", response_model=FairnessOut)
def get_fairness(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Показывает текущий публичный хеш сида — до того, как игрок сделал ставку."""
    fairness_service.ensure_seed_pair(db, user)
    return {
        "client_seed": user.client_seed,
        "server_seed_hash": user.server_seed_hash,
        "nonce": user.nonce,
    }


@router.post("/client-seed", response_model=FairnessOut)
def set_client_seed(
    payload: ClientSeedIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Игрок задаёт свой client_seed вручную (влияет на будущие ставки)."""
    fairness_service.ensure_seed_pair(db, user)
    user.client_seed = payload.client_seed.strip()[:64] or user.client_seed
    db.commit()
    db.refresh(user)
    return {
        "client_seed": user.client_seed,
        "server_seed_hash": user.server_seed_hash,
        "nonce": user.nonce,
    }


@router.post("/rotate", response_model=RotateSeedOut)
def rotate_seed(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Раскрывает текущий server_seed (можно проверить все прошлые ставки)
    и выдаёт новую пару на будущее.
    """
    fairness_service.ensure_seed_pair(db, user)
    return fairness_service.rotate_seed_pair(db, user)
