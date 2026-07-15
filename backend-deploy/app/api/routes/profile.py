"""
Роут профиля игрока.
Отдаёт данные для страницы Profile.tsx.
"""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserProfile

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=UserProfile)
def get_profile(user: User = Depends(get_current_user)):
    """Возвращает статистику текущего игрока."""
    return user
