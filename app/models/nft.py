"""
Таблицы для блока "Апгрейды" (Upgrades — Блок 7 на фронте).

NftCatalog     — витрина всех NFT, которые вообще существуют в игре
                 (редактируешь как админ: добавить новый NFT, поменять цену).
UserInventory  — какие конкретно NFT сейчас лежат у конкретного юзера.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class NftCatalog(Base):
    __tablename__ = "nft_catalog"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String)
    image_url: Mapped[str] = mapped_column(String)

    # Стоимость в монетах — используется, чтобы считать шанс апгрейда
    # (соотношение цены того, что отдаёшь, к цене того, что хочешь получить)
    value: Mapped[int] = mapped_column(Integer)


class UserInventory(Base):
    __tablename__ = "user_inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    nft_id: Mapped[int] = mapped_column(ForeignKey("nft_catalog.id"))

    # Откуда взялся предмет: "case" | "egg" | "upgrade" — полезно для истории
    source: Mapped[str] = mapped_column(String)

    obtained_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
