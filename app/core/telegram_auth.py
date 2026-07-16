"""
Проверка авторизации Telegram Mini App.

Как это работает простыми словами:
  1. Когда пользователь открывает твоё приложение внутри Telegram,
     Telegram передаёт фронту строку initData — там лежат данные юзера
     (id, имя, username) и специальная подпись "hash".
  2. Фронт отправляет эту строку нам на бэкенд.
  3. Мы своим токеном бота пересчитываем подпись и сравниваем с той,
     что прислал Telegram. Совпало — значит данные настоящие, юзер
     реально пришёл из Telegram, а не подделал их в браузере.

Алгоритм — официальный, из документации Telegram.
"""

import hashlib
import hmac
import json
from urllib.parse import parse_qsl

from app.core.config import settings


def parse_and_verify(init_data: str) -> dict | None:
    """
    Проверяет строку initData.
    Возвращает данные пользователя (dict), если подпись верна.
    Возвращает None, если подпись не совпала.
    """
    if not init_data:
        return None

    # Разбираем строку "ключ=значение&ключ=значение" в список пар
    pairs = dict(parse_qsl(init_data))

    # Достаём подпись и убираем её из проверяемых данных
    received_hash = pairs.pop("hash", None)
    if received_hash is None:
        return None

    # Собираем строку для проверки: сортируем ключи по алфавиту
    # и склеиваем как "ключ=значение" через перенос строки
    data_check_string = "\n".join(
        f"{key}={value}" for key, value in sorted(pairs.items())
    )

    # Считаем секретный ключ на основе токена бота
    secret_key = hmac.new(
        b"WebAppData", settings.BOT_TOKEN.encode(), hashlib.sha256
    ).digest()

    # Считаем нашу подпись
    calculated_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    # Сравниваем подписи безопасным способом
    if not hmac.compare_digest(calculated_hash, received_hash):
        return None

    # Поле "user" — это JSON-строка, разворачиваем её в объект
    user_raw = pairs.get("user")
    if not user_raw:
        return None

    try:
        user = json.loads(user_raw)
    except json.JSONDecodeError:
        return None

    return user
