from typing import Dict

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app.infrastructure.db.session import get_session
from app.application.services.scan_service import (
    bulk_ingest_scans,
    create_scan,
    detect_scan_anomalies,
    ingest_canonical_scan,
)

from app.schemas import BulkScanRequest, CanonicalScanIngestRequest, ScanCreateRequest

router = APIRouter(prefix="/scans", tags=["scans"])
v1_router = APIRouter(prefix="/api/v1/scans", tags=["scans"])


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


@v1_router.post("")
def ingest_scan_v1(
    request: CanonicalScanIngestRequest,
    response: Response,
    session: Session = Depends(get_session),
) -> Dict[str, object]:
    """Canonical RFID scan ingestion endpoint with idempotency handling."""
    scan, created = ingest_canonical_scan(
        session,
        device_id=request.device_id,
        operation_timestamp=request.operation_timestamp,
        rfid_code=request.rfid_code,
        signal_quality=request.signal_quality,
        idempotency_key=request.idempotency_key,
    )

    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return {
        "status": "created" if created else "duplicate",
        "scan": {
            "id": scan.id,
            "device_id": scan.device_id,
            "operation_timestamp": scan.scanned_at.isoformat(),
            "rfid_code": scan.rfid_code,
            "signal_quality": scan.signal_quality,
            "idempotency_key": scan.idempotency_key,
        },
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
