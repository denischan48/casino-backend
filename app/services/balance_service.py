"""
Сервис работы с балансом.

ПОМЕТКА ДЕНИСУ: это заготовка. Сюда позже переедет ВСЯ логика денег из фронта
(списание ставки, начисление выигрыша). Главный принцип казино:
деньги считает ТОЛЬКО сервер, а не браузер — иначе баланс можно накрутить.

Пока здесь одна простая безопасная функция изменения баланса.
"""

from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.user import User


def change_balance(db: Session, user: User, amount: int, title: str) -> User:
    """
    Меняет баланс пользователя и записывает операцию в историю.
    amount > 0 — начисление, amount < 0 — списание.
    """
    # Не даём уйти в минус
    if user.balance + amount < 0:
        raise ValueError("Недостаточно средств")

    user.balance += amount

    tx = Transaction(
        user_id=user.id,
        title=title,
        amount=amount,
        direction="in" if amount > 0 else "out",
    )
    db.add(tx)
    db.commit()
    db.refresh(user)
    return user
