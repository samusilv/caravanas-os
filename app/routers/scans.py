from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.database import get_session
from app.models import ReaderScan


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
