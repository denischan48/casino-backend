"""
Схемы (формы) данных пользователя.
Описывают, В КАКОМ ВИДЕ бэкенд отдаёт данные наружу, во фронт.
Названия полей совпадают с тем, что ждёт React.
"""

from pydantic import BaseModel


class UserProfile(BaseModel):
    """Данные для страницы Профиль."""
    telegram_id: int
    username: str | None
    first_name: str | None
    balance: int
    invites: int
    games_played: int
    top_win: int
    is_vip: bool

    # Разрешаем создавать схему прямо из объекта модели SQLAlchemy
    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """Ответ на запрос авторизации."""
    ok: bool
    user: UserProfile
