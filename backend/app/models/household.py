from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .household_member import HouseholdMember
    from .inventory_item import InventoryItem

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime
from sqlalchemy.sql import func

from app.db import Base


class Household(Base):
    """Gruppo/famiglia che condivide l'inventario."""
    __tablename__ = "households"

    # Chiave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Nome della famiglia (indicizzato)
    name: Mapped[str] = mapped_column(String(120), index=True)

    # Timestamp creato dal DB
    created_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relazione 1→N con HouseholdMember
    members: Mapped[list[HouseholdMember]] = relationship(
        back_populates="household",
        cascade="all, delete-orphan",
    )

    # Relazione 1→N con InventoryItem (gli oggetti “fisici” in casa)
    items: Mapped[list[InventoryItem]] = relationship(
        back_populates="household",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Household id={self.id} name={self.name}>"
