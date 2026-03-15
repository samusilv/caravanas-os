from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.database import get_session
from app.models import Animal, LotAnimal, ReaderScan


class BulkScanRequest(BaseModel):
    rfid_codes: List[str]
    reader_name: Optional[str] = None
    batch_id: Optional[str] = None


router = APIRouter(prefix="/scans", tags=["scans"])


@router.post("/bulk")
def bulk_scans(
    request: BulkScanRequest,
    session: Session = Depends(get_session),
) -> Dict[str, object]:
    """Ingest bulk RFID scans."""
    codes = [c.strip() for c in request.rfid_codes if c and c.strip()]
    if not codes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="rfid_codes must contain at least one non-empty value")

    # Deduplicate within request while preserving order
    seen = set()
    unique_codes: List[str] = []
    for code in codes:
        if code not in seen:
            seen.add(code)
            unique_codes.append(code)

    # Detect existing scans for this reader/batch to avoid duplicates
    stmt = select(ReaderScan.rfid_code).where(
        ReaderScan.rfid_code.in_(unique_codes)
    )
    if request.reader_name is not None:
        stmt = stmt.where(ReaderScan.reader_name == request.reader_name)
    if request.batch_id is not None:
        stmt = stmt.where(ReaderScan.batch_id == request.batch_id)

    existing = {row[0] for row in session.exec(stmt).all()}

    to_create = [
        ReaderScan(rfid_code=code, reader_name=request.reader_name, batch_id=request.batch_id)
        for code in unique_codes
        if code not in existing
    ]

    session.add_all(to_create)
    session.commit()

    return {
        "total_received": len(request.rfid_codes),
        "created_scans": len(to_create),
        "duplicated_codes": sorted(list(existing)),
    }


@router.get("/anomalies")
def scan_anomalies(*, session: Session = Depends(get_session)) -> Dict[str, object]:
    """Detect scan anomalies for operational monitoring."""
    # Fetch all scans
    scans = session.exec(select(ReaderScan).order_by(ReaderScan.scanned_at)).all()

    # Unknown RFID codes
    known_tags = {a.tag_id for a in session.exec(select(Animal)).all()}
    unknown_rfids = sorted({scan.rfid_code for scan in scans if scan.rfid_code not in known_tags})

    # Multi-scan within short period
    quick_window = timedelta(minutes=5)
    multi_scan_anomalies = []
    scans_by_code = {}
    for scan in scans:
        scans_by_code.setdefault(scan.rfid_code, []).append(scan.scanned_at)

    for code, timestamps in scans_by_code.items():
        timestamps.sort()
        group = []
        for idx in range(1, len(timestamps)):
            if timestamps[idx] - timestamps[idx - 1] <= quick_window:
                if not group:
                    group = [timestamps[idx - 1]]
                group.append(timestamps[idx])
            else:
                if group:
                    multi_scan_anomalies.append({"rfid_code": code, "timestamps": [t.isoformat() for t in group]})
                    group = []
        if group:
            multi_scan_anomalies.append({"rfid_code": code, "timestamps": [t.isoformat() for t in group]})

    # Scans outside active lots (animal exists but not assigned to any lot)
    animal_ids_in_lots = {la.animal_id for la in session.exec(select(LotAnimal)).all()}
    unassigned = []
    for scan in scans:
        # skip unknown
        if scan.rfid_code not in known_tags:
            continue
        animal = session.exec(select(Animal).where(Animal.tag_id == scan.rfid_code)).first()
        if animal and animal.id not in animal_ids_in_lots:
            unassigned.append({"rfid_code": scan.rfid_code, "animal_id": animal.id, "scanned_at": scan.scanned_at.isoformat()})

    return {
        "unknown_rfids": unknown_rfids,
        "multiple_quick_scans": multi_scan_anomalies,
        "unassigned_scans": unassigned,
    }
