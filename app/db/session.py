"""
Подключение к базе данных.
Здесь создаётся "движок" и способ получать сессию (соединение) с БД.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# connect_args нужен только для SQLite (разрешает работу из разных потоков).
# Для PostgreSQL эту строку можно убрать.
connect_args = (
    {"check_same_thread": False}
    if settings.DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

# "Фабрика" сессий — из неё берём соединение на каждый запрос
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Базовый класс. От него наследуются все модели таблиц."""
    pass


def get_db():
    """
    Выдаёт сессию БД на время одного запроса и закрывает её после.
    FastAPI вызывает эту функцию автоматически (через Depends).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
