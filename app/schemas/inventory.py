"""
Схемы для продажи NFT из инвентаря обратно казино (buyback 1:1).
"""

from pydantic import BaseModel


class InventorySellIn(BaseModel):
    inventory_id: int


class InventorySellOut(BaseModel):
    sold: bool
    amount: int
    new_balance: int
