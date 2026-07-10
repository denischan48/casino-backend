"""
Служебный файл Alembic. Обычно его не трогают руками.

Что делает: подключается к базе по адресу из твоего .env (через
app.core.config.settings) и сравнивает реальные таблицы с моделями
из app/models, чтобы понять, что изменилось.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Импортируем настройки и ВСЕ модели проекта (через __init__.py),
# чтобы Alembic видел полную картину таблиц.
from app.core.config import settings
from app.db.session import Base
import app.models  # noqa: F401  — импорт нужен, чтобы модели зарегистрировались

config = context.config

# Подставляем адрес базы из .env вместо значения из alembic.ini
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Это то, с чем Alembic сравнивает реальную базу
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
