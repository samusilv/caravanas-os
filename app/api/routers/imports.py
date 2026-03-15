from typing import Any, Dict

from fastapi import APIRouter, Depends, File, UploadFile
from sqlmodel import Session

from app.infrastructure.db.session import get_session
from app.application.services.scan_service import import_scans_csv

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("/scans-csv")
async def import_scans_csv_endpoint(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    """Import a CSV of RFID reader scans."""
    return import_scans_csv(session, file)
