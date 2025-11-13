from fastapi import FastAPI

# 1) Crea l'istanza FastAPI
app = FastAPI()

# 2) Importa i modelli senza sovrascrivere la variabile "app"
#    NOTA: prima probabilmente avevi "import app.models" (che rompeva tutto)
from app import models  # noqa: F401  # importato solo per i side-effect (registrare i modelli)

# 3) Importa i router
from app.api.routes import router as health_router
from app.api.auth import router as auth_router

# 4) Monta i router sull'app FastAPI
app.include_router(health_router, prefix="/api")
app.include_router(auth_router)  # ha già prefix="/api/auth" definito nel router

# 5) Rotta base di test
@app.get("/")
def read_root():
    return {"message": "Fridly API up!"}
