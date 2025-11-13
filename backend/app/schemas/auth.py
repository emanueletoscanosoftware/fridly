from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    """Dati attesi quando un utente si registra / fa login"""
    email: EmailStr
    password: str

class UserOut(BaseModel):
    """Cosa restituiamo quando mostriamo un utente (mai la password)"""
    model_config = ConfigDict(from_attributes=True) # consente di serializzare da oggetti ORM
    id: int
    email: EmailStr

class Token(BaseModel):
    """Formato del token che consegniamo al login"""
    access_token: str
    token_type: str = "bearer"