"""
Роут авторизации.
Фронт дёргает его один раз при запуске приложения, чтобы проверить вход
и получить данные пользователя.
"""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import AuthResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/telegram", response_model=AuthResponse)
def auth_telegram(user: User = Depends(get_current_user)):
    """
    Проверяет подпись Telegram (внутри get_current_user) и возвращает юзера.
    Если юзер зашёл впервые — он автоматически создаётся в базе.
    """
    return {"ok": True, "user": user}
