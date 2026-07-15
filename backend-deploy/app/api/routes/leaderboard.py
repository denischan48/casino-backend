"""
Роут лидерборда.
Отдаёт топ игроков по крупнейшему выигрышу для Leaderboard.tsx.

ПОМЕТКА ДЕНИСУ: пока сортируем просто по top_win из таблицы users.
Позже сюда добавим фильтры по времени (день / неделя / всё время) —
для этого нужна отдельная таблица выигрышей с датами.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.wallet import LeaderOut

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

# Заглушка-аватар, пока у юзеров нет своих
DEFAULT_AVATAR = "👤"


@router.get("", response_model=list[LeaderOut])
def get_leaderboard(
    timeframe: str = "week",  # день/неделя/всё — пока не влияет, задел на будущее
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Возвращает топ-20 игроков."""
    top_users = (
        db.query(User)
        .order_by(User.top_win.desc())
        .limit(20)
        .all()
    )

    result = []
    for i, u in enumerate(top_users, start=1):
        result.append(
            {
                "id": u.id,
                "rank": i,
                "username": f"@{u.username}" if u.username else "@anonym",
                "avatar": DEFAULT_AVATAR,
                "winAmount": f"{u.top_win:,}",
                "isVIP": u.is_vip,
            }
        )

    return result
