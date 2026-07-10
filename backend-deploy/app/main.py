"""
Точка входа бэкенда.
Запуск для разработки:
    uvicorn app.main:app --reload

После запуска открой в браузере http://127.0.0.1:8000/docs —
там автоматическая страница со всеми ручками API, где всё можно потыкать.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import Base, engine

# Подключаем все роуты
from app.api.routes import auth, profile, wallet, leaderboard

# Создаём таблицы в базе, если их ещё нет.
# ПОМЕТКА ДЕНИСУ: для простоты таблицы создаются автоматически при старте.
# На серьёзном проекте для этого используют миграции (Alembic) — добавим позже.
#

app = FastAPI(title="Casino TMA Backend")

# CORS — разрешаем фронту обращаться к нам.
# Без этого браузер заблокирует запросы с другого адреса.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Все ручки будут начинаться с /api
app.include_router(auth.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(wallet.router, prefix="/api")
app.include_router(leaderboard.router, prefix="/api")


@app.get("/")
def root():
    """Простая проверка, что сервер жив."""
    return {"status": "ok", "message": "Casino TMA backend работает"}
