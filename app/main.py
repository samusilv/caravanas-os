from fastapi import FastAPI

from app.database import init_db
from app.routers.health import router as health_router

app = FastAPI(title="CaravanaOS")


@app.on_event("startup")
def on_startup() -> None:
    """Initialize application resources on startup."""
    init_db()


app.include_router(health_router)
