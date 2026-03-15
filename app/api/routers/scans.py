from typing import Dict

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.infrastructure.db.session import get_session
from app.application.services.scan_service import bulk_ingest_scans, create_scan, detect_scan_anomalies

from app.schemas import BulkScanRequest, ScanCreateRequest

router = APIRouter(prefix="/scans", tags=["scans"])


@router.post("")
def register_scan(
    request: ScanCreateRequest,
    session: Session = Depends(get_session),
) -> Dict[str, object]:
    """Register a single RFID scan from a reader."""
    scan = create_scan(session, request.rfid_code, request.reader_name, request.batch_id)
    return {
        "id": scan.id,
        "rfid_code": scan.rfid_code,
        "reader_name": scan.reader_name,
        "batch_id": scan.batch_id,
        "scanned_at": scan.scanned_at.isoformat(),
    }


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
