"""
Схемы для раздела рефералки (главный экран, бонус центр, профиль).
"""

from datetime import datetime

from pydantic import BaseModel


class ReferralFriendOut(BaseModel):
    username: str | None
    first_name: str | None
    joined_at: datetime
    bonus_paid: bool


class ReferralMeOut(BaseModel):
    ref_code: str                  # telegram_id юзера строкой — фронт сам собирает ссылку
    invites_total: int             # для профиля/бонус центра — общий счётчик, не уменьшается
    invites_balance: int           # для главного экрана и выбора бонусного кейса — тратится
    referral_ton_balance: float    # накопленный бонус в TON, ожидает вывода
    min_withdraw_ton: float
    friends: list[ReferralFriendOut]
