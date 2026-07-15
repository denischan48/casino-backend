"""
Логика рефералки.

register_referral        — привязать нового юзера к пригласившему (один раз, при первом входе)
credit_first_deposit_bonus — начислить 10% рефереру с ПЕРВОГО пополнения приглашённого друга
spend_invites             — потратить баланс приглашений (например на бонусный кейс за 2 шт)

ПОМЕТКА ДЕНИСУ: credit_first_deposit_bonus готова, но пока никем не вызывается —
реальных пополнений (депозитов) в проекте ещё нет (Wallet.tsx сейчас с моками).
Как только сделаем настоящий эндпоинт пополнения — просто вызовем эту функцию
оттуда одной строкой, и рефералка заработает по-настоящему.
"""

from sqlalchemy.orm import Session

from app.models.referral import Referral
from app.models.user import User

REFERRAL_PERCENT = 0.10  # 10% с первого пополнения друга
MIN_WITHDRAW_TON = 10.0  # минимальная сумма для вывода реферального бонуса


def register_referral(db: Session, user: User, ref_code: str | None) -> bool:
    """
    Привязывает нового юзера к пригласившему. Вызывается один раз — при первом
    входе юзера в приложение. Если юзер уже когда-то был привязан (есть строка
    в referrals) — ничего не делает, повторно привязать нельзя.
    """
    if not ref_code:
        return False

    # уже привязан к кому-то раньше — не трогаем
    already_linked = db.query(Referral).filter(Referral.invited_id == user.id).first()
    if already_linked:
        return False

    try:
        inviter_telegram_id = int(ref_code)
    except ValueError:
        return False

    inviter = db.query(User).filter(User.telegram_id == inviter_telegram_id).first()
    if not inviter or inviter.id == user.id:
        return False  # сам себя пригласить нельзя, реф. код невалиден

    db.add(Referral(inviter_id=inviter.id, invited_id=user.id))
    inviter.invites += 1
    inviter.invites_balance += 1
    db.commit()
    return True


def credit_first_deposit_bonus(db: Session, invited_user: User, deposit_amount_ton: float) -> float | None:
    """
    Начисляет рефереру 10% от ПЕРВОГО пополнения приглашённого друга.
    Возвращает сумму бонуса в TON, либо None, если бонус уже был начислен
    раньше или юзер вообще не был приглашён по рефералке.
    """
    referral = (
        db.query(Referral)
        .filter(Referral.invited_id == invited_user.id, Referral.bonus_paid == False)  # noqa: E712
        .first()
    )
    if not referral:
        return None

    inviter = db.query(User).filter(User.id == referral.inviter_id).first()
    if not inviter:
        return None

    bonus = round(deposit_amount_ton * REFERRAL_PERCENT, 4)
    inviter.referral_ton_balance += bonus
    referral.bonus_paid = True
    db.commit()
    return bonus


def spend_invites(db: Session, user: User, amount: int) -> bool:
    """Списывает баланс приглашений (например при открытии бонусного кейса)."""
    if user.invites_balance < amount:
        return False
    user.invites_balance -= amount
    db.commit()
    return True
