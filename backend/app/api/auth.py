from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, UserOut, Token
from app.core.security import (
    hash_password, verify_password, create_access_token, SECRET_KEY, ALGORITHM
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Crea un nuovo utente:
    - controlla se l'email esiste già
    - salva la password HASHATA
    - restituisce i dati "sicuri" (UserOut)
    """
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email già registrata")
    
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Endpoint di login usato anche dal popup "Authorize" di Swagger.

    Swagger invia un form con:
    - username: noi lo useremo come email
    - password: la password in chiaro

    OAuth2PasswordRequestForm li incapsula in 'form_data'.
    """
    # prendiamo l'email dal campo "username" del form
    email = form_data.username

    # 1) cerchiamo l'utente per email
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        # stesso messaggio per email o password errata (più sicuro)
        raise HTTPException(status_code=400, detail="Credenziali non valide")

    # 2) creiamo il token con subject = id utente
    access_token = create_access_token(subject=user.id)
    return Token(access_token=access_token)


# Dice a FastAPI dove si ottiene il token (info per /docs). Noi accettiamo Bearer token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Prende il token dall'header Authorization: Bearer <token>,
    lo decodifica e carica l'utente dal DB
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub: str | None = payload.get("sub")
        if sub is None:
            raise HTTPException(status_code=401, detail="Token invalido")
    except JWTError:
        # firma sbagliata, scaduto, malformato...
        raise HTTPException(status_code=401, detail="Token invalido")
    
    # SQLAlchemy 2.x: usa db.get(Modello, pk) per caricare per PK
    user = db.get(User, int(sub))
    if not user:
        raise HTTPException(status_code=401, detail="Utente non trovato")
    return user

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    """
    Ritorna l'utente "loggato" (derivato dal token)
    Se il token è assente -> 401 automatico
    """
    return current_user