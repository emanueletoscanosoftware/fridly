from typing import List
from pydantic import BaseModel, EmailStr, ConfigDict

# Questo schema rappresenta i dati necessari per CREARE una nuova casa.
# Per ora ci serve solo il nome, ma in futuro potremmo aggiungere altro (es. icona, colore).
class HouseholdCreate(BaseModel):
    name: str # nome scelto dall'utente

# Questo schema rappresenta un "membro" di una casa
# così come lo vogliamo restituire nelle API (id, email, ruolo).
class HouseholdMemberOut(BaseModel):
    id: int           # id dell'utente (User.id)   
    email: EmailStr   # email dell'utente
    role: str         # ruolo nella casa: es. "owner" o "member"

# Questo schema rappresenta una casa completa di membri.
class HouseholdOut(BaseModel):
    model_config = ConfigDict(from_attributes=True) # permette di creare l'oggetto da modelli ORM
    id: int                             # id della casa (Household.id)
    name: str                           # nome della casa
    members: List[HouseholdMemberOut]   # lista dei membri della casa

# Schema per la richiesta di invito: per aggiungere un membro usiamo la sua email.
class HouseholdInvite(BaseModel):
    email: EmailStr       # email dell'utente già registrato da aggiungere alla casa  
    role: str = "member"  # ruolo nella casa; default = "member"

"""
Perché questi quattro schemi?
HouseholdCreate → cosa ci manda il client quando fa POST /households.
HouseholdOut → come vogliamo restituire una casa (id, name, members).
HouseholdMemberOut → come descriviamo ogni membro nella risposta.
HouseholdInvite → cosa ci manda il client per aggiungere qualcuno a una casa.
"""