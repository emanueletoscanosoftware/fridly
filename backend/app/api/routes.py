# sottomodulo di rotte
from fastapi import APIRouter

# creazione router, separazione delle routes per area, più ordinato e scalabile
router = APIRouter()

# creazione route GET su /health dentro questo router
@router.get("/health")
def healthcheck():
    return {"status": "ok"}
