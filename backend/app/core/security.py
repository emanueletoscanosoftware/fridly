import os
from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext
from jose import jwt

# Prendiamo i valori dal .env
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# QUI il cambiamento:
# prima usavamo schemes=["bcrypt"], che richiede il modulo bcrypt problematico.
# Ora usiamo pbkdf2_sha256, che è robusto e non dipende da bcrypt esterno.
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
)

def hash_password(password: str) -> str:
    """
    Trasforma la password in un hash (impronta) usando pbkdf2_sha256.
    L'hash è una stringa che contiene anche info su algoritmo e parametri.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se la password in chiaro corrisponde all'hash.
    Passlib si occupa di:
    - prendere algoritmo/parametri dall'hash
    - rifare il calcolo
    - confrontare in modo sicuro.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(subject: str | int) -> str:
    """
    Crea un JWT con:
    - 'sub' = subject (chi è l'utente, di solito id)
    - 'exp' = scadenza
    Lo firma con SECRET_KEY + ALGORITHM, così non può essere alterato.
    """
    expire = datetime.now(tz=timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(subject), "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token
