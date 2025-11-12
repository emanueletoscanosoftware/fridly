from __future__ import annotations

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.db import Base, engine, SessionLocal
import app.models as m

# Carica .env
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

def main() -> None:
    # ATTENZIONE: in produzione usa solo Alembic; create_all è ok per dev/seed
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db: 
        u = m.User(email="demo@fridly.test", hashed_password="HASH_FINTA")
        db.add(u); db.commit(); db.refresh(u)

        hh = m.Household(name="Casa Demo")
        db.add(hh); db.commit(); db.refresh(hh)

        mm = m.HouseholdMember(user_id=u.id, household_id=hh.id, role="owner")
        db.add(mm); db.commit()

    print("Seed ok.")

if __name__ == "__main__":
    main()
