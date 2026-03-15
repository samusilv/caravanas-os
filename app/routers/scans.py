from typing import Dict

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.services.scan_service import bulk_ingest_scans, detect_scan_anomalies

from app.schemas import BulkScanRequest

router = APIRouter(prefix="/scans", tags=["scans"])


@router.post("/bulk")
def bulk_scans(
    request: BulkScanRequest,
    session: Session = Depends(get_session),
) -> Dict[str, object]:
    """Ingest bulk RFID scans."""
    return bulk_ingest_scans(session, request.rfid_codes, request.reader_name, request.batch_id)


@router.get("/anomalies")
def scan_anomalies(*, session: Session = Depends(get_session)) -> Dict[str, object]:
    """Detect scan anomalies for operational monitoring."""
    return detect_scan_anomalies(session)
