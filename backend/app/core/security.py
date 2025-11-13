import os
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt

# 1) Config letta dal .env (già caricato dal progetto)
SECRET_KEY = os.getenv("SECRET KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# 2) 'pwd_context' sa come hashare e verificare password (usiamo bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Trasforma la password in un hash"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Controlla se la password in chiaro combacia con l'hash salvato"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(subject: str | int) -> str:
    """
    Crea un JWT (JSON Web Token) firmato
    - 'sub' = subject (chi sei: di solito l'ID utente)
    - 'exp' = tempo di scadenza (dopo questo, il token non vale più)
    """
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(subject), "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token