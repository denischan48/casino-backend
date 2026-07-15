"""
Роут рефералки.

  GET /referral/me — вся статистика для главного экрана/профиля/бонус центра:
                      реф-код, счётчик приглашённых, баланс приглашений,
                      накопленный TON-бонус, список друзей.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.referral import Referral
from app.models.user import User
from app.schemas.referral import ReferralFriendOut, ReferralMeOut
from app.services.referral_service import MIN_WITHDRAW_TON

router = APIRouter(prefix="/referral", tags=["referral"])


@router.get("/me", response_model=ReferralMeOut)
def get_my_referral_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Referral, User)
        .join(User, User.id == Referral.invited_id)
        .filter(Referral.inviter_id == user.id)
        .order_by(Referral.created_at.desc())
        .all()
    )

    friends = [
        ReferralFriendOut(
            username=friend.username,
            first_name=friend.first_name,
            joined_at=referral.created_at,
            bonus_paid=referral.bonus_paid,
        )
        for referral, friend in rows
    ]

    return {
        "ref_code": str(user.telegram_id),
        "invites_total": user.invites,
        "invites_balance": user.invites_balance,
        "referral_ton_balance": user.referral_ton_balance,
        "min_withdraw_ton": MIN_WITHDRAW_TON,
        "friends": friends,
    }
