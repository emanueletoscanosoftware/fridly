# Abilita comportamento moderno delle annotazioni (evita stringhe nei tipi)
from __future__ import annotations

# Import solo per il type-checker (non eseguiti a runtime)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .household_member import HouseholdMember  # usato nelle annotazioni

# Import SQLAlchemy (API 2.x tipate)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.sql import func

# Base comune dei modelli (dichiarata in app/db.py)
from app.db import Base


class User(Base):
    """Tabella utenti dell'app."""
    __tablename__ = "users"

    # Chiave primaria intera, indicizzata
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Email univoca (max 255) e indicizzata
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    # Password hashata (mai in chiaro)
    hashed_password: Mapped[str] = mapped_column(String(255))

    # Utente attivo sì/no (default True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamp creato dal DB al momento dell'inserimento
    created_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relazione 1→N con HouseholdMember (lati "python")
    # list[...] è il generic built-in; niente stringhe nei tipi grazie a __future__
    memberships: Mapped[list[HouseholdMember]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
