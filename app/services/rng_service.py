"""
Provably Fair — честная генерация результата, которую игрок может проверить сам.

Как это устроено (пара сидов на игрока):
  server_seed       — секретное число, знает только сервер
  server_seed_hash  — его хеш (SHA-256), показываем игроку ЗАРАНЕЕ, до ставок
  client_seed       — игрок может задать свой (по умолчанию генерируем сами)
  nonce             — счётчик ставок, растёт на 1 после каждой игры

Результат каждой ставки считается не голым random(), а хешем от связки
server_seed + client_seed + nonce. Поскольку server_seed_hash был показан
ДО того, как сыграна ставка — сервер физически не может задним числом
подменить server_seed под нужный ему исход: хеш бы не совпал.
"""

import hashlib
import hmac
import secrets


def generate_server_seed() -> str:
    """Генерирует новый секретный сид сервера."""
    return secrets.token_hex(32)


def generate_client_seed() -> str:
    """Сид по умолчанию для игрока, если он не задал свой."""
    return secrets.token_hex(8)


def hash_seed(seed: str) -> str:
    """SHA-256 от сида — вот что показываем игроку заранее."""
    return hashlib.sha256(seed.encode()).hexdigest()


def roll(server_seed: str, client_seed: str, nonce: int) -> float:
    """
    Возвращает число 0.00–99.99 — детерминированное для конкретной
    связки (server_seed, client_seed, nonce). Используется в монетке и дайсе.
    """
    message = f"{client_seed}:{nonce}"
    digest = hmac.new(server_seed.encode(), message.encode(), hashlib.sha256).hexdigest()
    num = int(digest[:8], 16)
    return round((num / 0xFFFFFFFF) * 100, 2)


def shuffled_positions(server_seed: str, client_seed: str, nonce: int, n: int = 25) -> list[int]:
    """
    Честная перетасовка позиций 0..n-1 — используется в минах, чтобы решить,
    где заминированные клетки. Тот же принцип, что и roll(): детерминировано
    по (server_seed, client_seed, nonce), поэтому проверяемо игроком.

    Алгоритм — классический Fisher-Yates shuffle, только вместо обычного
    random() на каждом шаге берём число из хеша.
    """
    indices = list(range(n))
    for i in range(n - 1, 0, -1):
        message = f"{client_seed}:{nonce}:{i}"
        digest = hmac.new(server_seed.encode(), message.encode(), hashlib.sha256).hexdigest()
        r = int(digest[:8], 16)
        j = r % (i + 1)
        indices[i], indices[j] = indices[j], indices[i]
    return indices
