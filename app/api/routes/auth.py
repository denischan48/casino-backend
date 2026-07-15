"""
Роут авторизации.
Фронт дёргает его один раз при запуске приложения, чтобы проверить вход
и получить данные пользователя.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import AuthResponse
from app.services.referral_service import register_referral

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/telegram", response_model=AuthResponse)
def auth_telegram(
    ref: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Проверяет подпись Telegram (внутри get_current_user) и возвращает юзера.
    Если юзер зашёл впервые — он автоматически создаётся в базе.

    ПОМЕТКА ДЕНИСУ: параметр ref — это telegram_id пригласившего, фронт берёт
    его из Telegram.WebApp.initDataUnsafe.start_param и передаёт сюда как
    query-параметр: POST /api/auth/telegram?ref=123456789
    Привязка происходит только один раз — если юзер уже был кем-то приглашён
    раньше, повторный вызов с другим ref ничего не поменяет.
    """
    register_referral(db, user, ref)
    return {"ok": True, "user": user}
