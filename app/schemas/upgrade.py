"""
Схемы для раздела "Апгрейды" — версия с апгрейдом сразу нескольких предметов
(цель и шанс считаются от их суммарной стоимости).
"""

from pydantic import BaseModel


class UpgradeTargetOut(BaseModel):
    """Один из возможных вариантов, во что можно апгрейднуть сумму предметов."""
    nft_id: int
    name: str
    image_url: str
    value: int
    chance: float  # шанс успеха в %, например 21.25


class UpgradeAttemptIn(BaseModel):
    inventory_item_ids: list[int]  # какие предметы из user_inventory рискуем (можно несколько)
    target_nft_id: int             # во что целимся (id из nft_catalog)


class UpgradeResultItemOut(BaseModel):
    name: str
    image_url: str
    value: int


class UpgradeAttemptOut(BaseModel):
    win: bool
    chance: float
    roll: float
    result_item: UpgradeResultItemOut | None = None    # заполнено только при победе
    lost_items: list[UpgradeResultItemOut] | None = None  # заполнено только при проигрыше
    nonce: int
    server_seed_hash: str
