import csv
from io import TextIOWrapper
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlmodel import Session

from app.database import get_session
from app.models import ReaderScan

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("/scans-csv")
async def import_scans_csv(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    """Import a CSV of RFID reader scans.

    Expected columns:
    - rfid_code (required)
    - reader_name (optional)
    - batch_id (optional)

    The endpoint ignores empty rows and returns a report of imported/skipped rows.
    """
    if file.content_type not in ("text/csv", "application/vnd.ms-excel", "text/plain"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a CSV")

    decoded = TextIOWrapper(file.file, encoding="utf-8")
    reader = csv.DictReader(decoded)

    total_rows = 0
    imported_rows = 0
    skipped_rows = 0
    errors: List[Dict[str, Any]] = []

    for row_num, row in enumerate(reader, start=1):
        total_rows += 1

        # Skip completely empty rows
        if not any(value and value.strip() for value in row.values()):
            skipped_rows += 1
            continue

        rfid_code = (row.get("rfid_code") or "").strip()
        if not rfid_code:
            skipped_rows += 1
            errors.append({"row": row_num, "error": "Missing rfid_code"})
            continue

        reader_name = (row.get("reader_name") or "").strip() or None
        batch_id = (row.get("batch_id") or "").strip() or None

        scan = ReaderScan(rfid_code=rfid_code, reader_name=reader_name, batch_id=batch_id)
        session.add(scan)
        try:
            session.commit()
            imported_rows += 1
        except Exception as exc:  # noqa: BLE001
            session.rollback()
            skipped_rows += 1
            errors.append({"row": row_num, "error": str(exc)})

    return {
        "total_rows": total_rows,
        "imported_rows": imported_rows,
        "skipped_rows": skipped_rows,
        "errors": errors,
    }
