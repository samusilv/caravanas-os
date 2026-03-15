from fastapi import FastAPI

from app.database import init_db
from app.routers.animals import router as animals_router
from app.routers.events import router as events_router
from app.routers.health import router as health_router
from app.routers.imports import router as imports_router
from app.routers.lots import router as lots_router
from app.routers.root import router as root_router
from app.routers.scans import router as scans_router

app = FastAPI(title="CaravanaOS")


@app.on_event("startup")
def on_startup() -> None:
    """Initialize application resources on startup."""
    init_db()


app.include_router(root_router)
app.include_router(health_router)
app.include_router(animals_router)
app.include_router(events_router)
app.include_router(imports_router)
app.include_router(scans_router)
app.include_router(lots_router)
