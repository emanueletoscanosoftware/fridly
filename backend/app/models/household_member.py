from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User
    from .household import Household

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, UniqueConstraint

from app.db import Base


class HouseholdMember(Base):
    """
    Tabella ponte User<->Household con ruolo (es. owner/member).
    Garantisce unicità della coppia (user_id, household_id).
    """
    __tablename__ = "household_members"

    # Vincolo di unicità sulla coppia utente-famiglia
    __table_args__ = (
        UniqueConstraint("user_id", "household_id", name="uq_user_household"),
    )

    # Chiave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # FK verso users.id (cancella membership se l'utente sparisce)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    # FK verso households.id (cancella membership se la famiglia sparisce)
    household_id: Mapped[int] = mapped_column(
        ForeignKey("households.id", ondelete="CASCADE"), index=True
    )

    # Ruolo all'interno dell'household (owner/member)
    role: Mapped[str] = mapped_column(String(20), default="member")

    # Lati delle relazioni ORM (oggetti Python collegati)
    user: Mapped[User] = relationship(back_populates="memberships")
    household: Mapped[Household] = relationship(back_populates="members")

    def __repr__(self) -> str:
        return f"<HouseholdMember user={self.user_id} hh={self.household_id} role={self.role}>"
