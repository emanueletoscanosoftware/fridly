from fastapi import FastAPI

app = FastAPI()

from app import models  # noqa: F401
from app.api.routes import router as health_router
from app.api.auth import router as auth_router
from app.api.households import router as household_router  # <--- nuovo

app.include_router(health_router, prefix="/api")
app.include_router(auth_router)
app.include_router(household_router)  # <--- nuovo

@app.get("/")
def read_root():
    return {"message": "Fridly API up!"}
