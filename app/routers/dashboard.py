from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.services.dashboard_service import get_dashboard_summary as service_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(*, session: Session = Depends(get_session)) -> dict:
    """Return a small operational summary for the dashboard."""
    return service_dashboard_summary(session)
