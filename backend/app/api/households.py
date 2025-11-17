# app/api/households.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Importiamo il "come ottenere una sessione DB"
from app.db import get_db

# Importiamo i modelli ORM che useremo
from app.models.household import Household
from app.models.household_member import HouseholdMember
from app.models.user import User

# Importiamo la funzione che ci dice chi è l'utente loggato (dal router auth)
from app.api.auth import get_current_user

# Importiamo gli schemi Pydantic appena creati
from app.schemas.household import (
    HouseholdCreate,
    HouseholdOut,
    HouseholdMemberOut,
    HouseholdInvite,
)

# Creiamo un router dedicato alle rotte degli households
router = APIRouter(
    prefix="/api/households",  # tutte le rotte inizieranno con /api/households
    tags=["households"],       # nome del gruppo nelle API docs
)

def serialize_household(hh: Household) -> HouseholdOut:
    """
    Converte un oggetto Household (ORM) in HouseholdOut (Pydantic).
    Qui 'smontiamo' la relazione household.members -> user/email/role.
    """
    members_data: List[HouseholdMemberOut] = []

    for membership in hh.members:
        # membership è un HouseholdMember
        user: User = membership.user  # utente collegato a quella membership

        members_data.append(
            HouseholdMemberOut(
                id=user.id,
                email=user.email,
                role=membership.role,
            )
        )

    return HouseholdOut(
        id=hh.id,
        name=hh.name,
        members=members_data,
    )

@router.get("/", response_model=List[HouseholdOut])
def list_households(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Restituisce tutte le case di cui l'utente loggato è membro.
    - Usiamo una JOIN tra Household e HouseholdMember
    - Filtriamo per HouseholdMember.user_id == current_user.id
    """
    households = (
        db.query(Household)
        .join(HouseholdMember)
        .filter(HouseholdMember.user_id == current_user.id)
        .all()
    )

    # Convertiamo ogni Household in HouseholdOut tramite l'helper
    return [serialize_household(hh) for hh in households]

@router.post("/", response_model=HouseholdOut, status_code=status.HTTP_201_CREATED)
def create_household(
    payload: HouseholdCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Crea una nuova casa e rende l'utente corrente "owner".
    Passi:
    1. creiamo Household (solo con il nome)
    2. creiamo HouseholdMember che collega current_user a quella casa con role="owner"
    """
    # 1) Creiamo l'oggetto Household
    hh = Household(name=payload.name)
    db.add(hh)
    db.commit()
    db.refresh(hh)  # aggiorna hh con id assegnato dal DB

    # 2) Creiamo la membership per il creatore, ruolo owner
    membership = HouseholdMember(
        user_id=current_user.id,
        household_id=hh.id,
        role="owner",
    )
    db.add(membership)
    db.commit()
    db.refresh(hh)  # ricarichiamo hh così da vedere hh.members aggiornato

    # Importante: accediamo a hh.members così SQLAlchemy carica i membri
    _ = hh.members

    return serialize_household(hh)

def get_membership_or_404(
    db: Session, household_id: int, user_id: int
) -> HouseholdMember:
    """
    Ritorna la membership (HouseholdMember) se l'utente appartiene a quella casa.
    Se non appartiene, solleva 404 (casa non trovata per quell'utente).
    """
    membership = (
        db.query(HouseholdMember)
        .filter(
            HouseholdMember.household_id == household_id,
            HouseholdMember.user_id == user_id,
        )
        .first()
    )

    if not membership:
        # 404: dal punto di vista dell'utente, quella casa "non esiste"
        raise HTTPException(status_code=404, detail="Household non trovata")

    return membership

@router.get("/{household_id}", response_model=HouseholdOut)
def get_household(
    household_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Restituisce i dettagli di una singola casa (se l'utente ne è membro).
    Usa get_membership_or_404 per verificare che l'utente appartenga alla casa.
    """
    # Verifica membership (404 se non appartiene)
    _membership = get_membership_or_404(db, household_id, current_user.id)

    # Ora possiamo caricare la casa
    hh = db.query(Household).get(household_id)
    if not hh:
        raise HTTPException(status_code=404, detail="Household non trovata")

    # assicuriamoci che i membri siano caricati
    _ = hh.members

    return serialize_household(hh)

@router.post("/{household_id}/members", response_model=HouseholdOut)
def add_member(
    household_id: int,
    payload: HouseholdInvite,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Aggiunge un utente già registrato alla casa, tramite email.
    Solo chi ha ruolo 'owner' può farlo.
    Passi:
    1. controlla che current_user sia 'owner' della casa
    2. trova l'utente da aggiungere per email
    3. controlla che non sia già membro
    4. crea HouseholdMember e restituisce la casa aggiornata
    """
    # 1) membership dell'utente corrente
    my_membership = get_membership_or_404(db, household_id, current_user.id)
    if my_membership.role != "owner":
        # 403: Forbidden -> ha accesso alla casa ma non i permessi
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo il proprietario può aggiungere membri",
        )

    # 2) trova l'utente da invitare tramite email
    user_to_add = db.query(User).filter(User.email == payload.email).first()
    if not user_to_add:
        raise HTTPException(
            status_code=404,
            detail="Utente con questa email non trovato",
        )

    # 3) controlla che non sia già membro di quella casa
    existing = (
        db.query(HouseholdMember)
        .filter(
            HouseholdMember.household_id == household_id,
            HouseholdMember.user_id == user_to_add.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Utente già membro di questa casa")

    # 4) crea la nuova membership
    membership = HouseholdMember(
        user_id=user_to_add.id,
        household_id=household_id,
        role=payload.role,
    )
    db.add(membership)
    db.commit()

    # ricarica la casa con i membri aggiornati
    hh = db.query(Household).get(household_id)
    _ = hh.members

    return serialize_household(hh)
