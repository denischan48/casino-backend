"""
Общая зависимость авторизации.

Задача: на каждый защищённый запрос достать текущего пользователя.
Фронт присылает подпись Telegram в заголовке:
    Authorization: tma <initData>

Здесь мы:
  1. Берём initData из заголовка.
  2. Проверяем подпись (telegram_auth).
  3. Находим пользователя в базе или создаём нового, если это первый вход.
  4. Возвращаем объект User в роут.
"""

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.telegram_auth import parse_and_verify
from app.db.session import get_db
from app.models.user import User


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    tg_user = None

    # --- РЕЖИМ ОТЛАДКИ ---
    # ПОМЕТКА ДЕНИСУ: пока DEBUG=true в .env, можно тестировать API без Telegram.
    # Бэкенд подставит тестового пользователя. На реальном сервере поставь DEBUG=false.
    if settings.DEBUG and (not authorization or authorization == "tma debug"):
        tg_user = {"id": 111111, "username": "test_user", "first_name": "Денис"}

    # --- ОБЫЧНЫЙ РЕЖИМ ---
    else:
        if not authorization or not authorization.startswith("tma "):
            raise HTTPException(status_code=401, detail="Нет авторизации Telegram")

        init_data = authorization.removeprefix("tma ").strip()
        tg_user = parse_and_verify(init_data)

        if tg_user is None:
            raise HTTPException(status_code=401, detail="Подпись Telegram неверна")

    # Ищем пользователя в базе по telegram_id
    user = db.query(User).filter(User.telegram_id == tg_user["id"]).first()

    # Если такого нет — создаём (первый вход)
    if user is None:
        user = User(
            telegram_id=tg_user["id"],
            username=tg_user.get("username"),
            first_name=tg_user.get("first_name"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user
