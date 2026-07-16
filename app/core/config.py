"""
Настройки приложения.
Читаются автоматически из файла .env (см. .env.example).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Токен бота — нужен для проверки подписи Telegram
    BOT_TOKEN: str = ""

    # Строка подключения к базе (по умолчанию — файл sqlite)
    DATABASE_URL: str = "sqlite:///./casino.db"

    # Список разрешённых адресов фронта (CORS), приходит строкой через запятую.
    # Сразу вписан твой домен на Cybrancee + локальные адреса для разработки.
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,https://1999anemycase.xyz"

    # Режим отладки
    DEBUG: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_list(self) -> list[str]:
        """Превращает 'a,b,c' в ['a', 'b', 'c']."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


# Один общий объект настроек на всё приложение
settings = Settings()
