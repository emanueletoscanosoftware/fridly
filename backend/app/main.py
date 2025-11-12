# Importa la classe FastAPI
from fastapi import FastAPI
# Prende l'oggetto router creato prima; i file __init__.py anche se vuoti diconono a Python che /app e app/api/ sono package importabili
from app.api.routes import router as api_router
import app.models  # necessario per far "vedere" i modelli ad Alembic

# Creazione istanza FastAPI
app = FastAPI()

# Aggancia tutte le routes del router sotto il percorso /api
app.include_router(api_router, prefix="/api")

# Decoratore: gestore della rotta GET
@app.get("/") # tipo di richiesta (leggere dati)
def read_root():
    return {"message": "Fridly API up!"} # FastAPI trasforma il dizionario in JSON automaticamente