"""
Управление парой сидов (server_seed / client_seed) конкретного игрока.
Сама генерация чисел — в rng_service.py, здесь только работа с базой.
"""

from sqlalchemy.orm import Session

from app.models.user import User
from app.services import rng_service


def ensure_seed_pair(db: Session, user: User) -> User:
    """Если у игрока ещё нет пары сидов (первый заход) — создаём."""
    if not user.server_seed:
        user.server_seed = rng_service.generate_server_seed()
        user.server_seed_hash = rng_service.hash_seed(user.server_seed)
        user.client_seed = rng_service.generate_client_seed()
        user.nonce = 0
        db.commit()
        db.refresh(user)
    return user


def rotate_seed_pair(db: Session, user: User) -> dict:
    """
    Раскрывает текущий server_seed (чтобы игрок мог проверить прошлые ставки)
    и сразу генерирует новую пару на будущее.
    """
    revealed_seed = user.server_seed
    revealed_hash = user.server_seed_hash

    user.server_seed = rng_service.generate_server_seed()
    user.server_seed_hash = rng_service.hash_seed(user.server_seed)
    user.nonce = 0
    db.commit()
    db.refresh(user)

    return {
        "revealed_server_seed": revealed_seed,
        "revealed_server_seed_hash": revealed_hash,
        "new_server_seed_hash": user.server_seed_hash,
    }


def next_roll(db: Session, user: User) -> tuple[float, int]:
    """
    Считает следующий честный результат (0.00-99.99) для игрока и увеличивает
    nonce. Используется в монетке и дайсе.
    """
    ensure_seed_pair(db, user)
    used_nonce = user.nonce
    result = rng_service.roll(user.server_seed, user.client_seed, used_nonce)
    user.nonce += 1
    db.commit()
    db.refresh(user)
    return result, used_nonce


def next_shuffle(db: Session, user: User, n: int = 25) -> tuple[list[int], int]:
    """
    Честная раскладка позиций для мин. Увеличивает nonce так же, как next_roll —
    у игрока один общий счётчик ставок на все игры.
    """
    ensure_seed_pair(db, user)
    used_nonce = user.nonce
    positions = rng_service.shuffled_positions(user.server_seed, user.client_seed, used_nonce, n)
    user.nonce += 1
    db.commit()
    db.refresh(user)
    return positions, used_nonce
