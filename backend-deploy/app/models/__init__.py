"""
ПОМЕТКА ДЕНИСУ: этот файл нужен, чтобы SQLAlchemy и Alembic "увидели" все
таблицы разом. Если добавишь новый файл модели в эту папку — обязательно
добавь и сюда строку импорта, иначе таблица не создастся и Alembic не
заметит её при автогенерации миграции.
"""

from app.models.user import User
from app.models.transaction import Transaction
from app.models.bet import GameRound
from app.models.case import Case, CaseItem
from app.models.egg import Egg, EggItem
from app.models.nft import NftCatalog, UserInventory
from app.models.referral import Referral
from app.models.contest import Contest, ContestParticipant
from app.models.admin import Admin

__all__ = [
    "User",
    "Transaction",
    "GameRound",
    "Case",
    "CaseItem",
    "Egg",
    "EggItem",
    "NftCatalog",
    "UserInventory",
    "Referral",
    "Contest",
    "ContestParticipant",
    "Admin",
]
