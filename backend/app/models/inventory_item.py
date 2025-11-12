from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .product import Product
    from .household import Household

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db import Base


class InventoryItem(Base):
    """
    Istanza “fisica” di un prodotto nella casa:
    quanto ne hai, dove si trova, quando scade.
    """
    __tablename__ = "inventory_items"

    # Chiave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # A quale household appartiene l'item (FK → households.id)
    household_id: Mapped[int] = mapped_column(
        ForeignKey("households.id", ondelete="CASCADE"), index=True
    )

    # Quale prodotto è (FK → products.id)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), index=True
    )

    # Quantità (es. 1 confezione, 500 g...) e unità (pz/g/ml)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit: Mapped[str] = mapped_column(String(8), default="pz")

    # Data di scadenza (opzionale) e posizione (dispensa/frigo/freezer)
    expires_at: Mapped[Date | None] = mapped_column(Date, nullable=True)
    location: Mapped[str] = mapped_column(String(16), default="pantry")

    # Timestamp di inserimento creato dal DB
    added_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Lati delle relazioni ORM
    product: Mapped[Product] = relationship(back_populates="items")
    household: Mapped[Household] = relationship(back_populates="items")

    def __repr__(self) -> str:
        return f"<InventoryItem id={self.id} hh={self.household_id} prod={self.product_id}>"
