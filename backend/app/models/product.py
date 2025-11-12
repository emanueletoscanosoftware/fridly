from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .inventory_item import InventoryItem

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime
from sqlalchemy.sql import func

from app.db import Base


class Product(Base):
    """Catalogo generale dei prodotti (es. Pasta 500g, Latte 1L)."""
    __tablename__ = "products"

    # Chiave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Codice a barre (EAN) opzionale, unico e indicizzato
    ean: Mapped[str | None] = mapped_column(String(32), unique=True, index=True, nullable=True)

    # Nome del prodotto (indicizzato per ricerche testuali)
    name: Mapped[str] = mapped_column(String(255), index=True)

    # Brand e categoria opzionali (liberi per MVP)
    brand: Mapped[str | None] = mapped_column(String(120), nullable=True)
    category: Mapped[str | None] = mapped_column(String(120), nullable=True)

    # Timestamp creato dal DB
    created_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relazione 1→N con gli item fisici (presenti nelle case)
    items: Mapped[list[InventoryItem]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} ean={self.ean} name={self.name}>"
