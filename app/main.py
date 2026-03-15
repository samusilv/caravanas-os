from fastapi import FastAPI

from app.infrastructure.db.session import init_db
from app.api.routers.ai import router as ai_router
from app.api.routers.animals import router as animals_router
from app.api.routers.events import router as events_router
from app.api.routers.health import router as health_router
from app.api.routers.dashboard import router as dashboard_router
from app.api.routers.imports import router as imports_router
from app.api.routers.lots import router as lots_router
from app.api.routers.root import router as root_router
from app.api.routers.scans import router as scans_router, v1_router as scans_v1_router
from app.api.routers.exports import router as exports_router

app = FastAPI(title="CaravanaOS")


@app.on_event("startup")
def on_startup() -> None:
    """Initialize application resources on startup."""
    init_db()


# Legacy routes (temporary backward compatibility)
app.include_router(root_router)
app.include_router(health_router)
app.include_router(animals_router)
app.include_router(events_router)
app.include_router(imports_router)
app.include_router(scans_router)
app.include_router(scans_v1_router)
app.include_router(exports_router)
app.include_router(lots_router)
app.include_router(dashboard_router)
app.include_router(ai_router)

# Versioned routes
app.include_router(root_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")
app.include_router(animals_router, prefix="/api/v1")
app.include_router(events_router, prefix="/api/v1")
app.include_router(imports_router, prefix="/api/v1")
app.include_router(scans_router, prefix="/api/v1")
app.include_router(scans_v1_router, prefix="/api/v1")
app.include_router(exports_router, prefix="/api/v1")
app.include_router(lots_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
