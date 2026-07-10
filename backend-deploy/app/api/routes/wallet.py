"""
Роут кошелька.
Отдаёт баланс и историю транзакций для Wallet.tsx.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.wallet import WalletOut

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get("", response_model=WalletOut)
def get_wallet(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Возвращает текущий баланс и последние операции."""
    # Берём последние 20 транзакций пользователя, свежие сверху
    rows = (
        db.query(Transaction)
        .filter(Transaction.user_id == user.id)
        .order_by(Transaction.created_at.desc())
        .limit(20)
        .all()
    )

    # Превращаем строки базы в формат, который ждёт фронт
    history = [
        {
            "id": t.id,
            "title": t.title,
            # Форматируем сумму со знаком и разделителями тысяч
            "amount": f"{'+' if t.direction == 'in' else '-'}{abs(t.amount):,}",
            "date": t.created_at.strftime("%d.%m.%Y %H:%M"),
            "type": t.direction,
        }
        for t in rows
    ]

    return {"balance": user.balance, "history": history}
