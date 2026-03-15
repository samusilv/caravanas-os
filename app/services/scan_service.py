import csv
from datetime import datetime, timedelta
from io import TextIOWrapper
from typing import Any, Dict, List

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models import Animal, LotAnimal, ReaderScan


def import_scans_csv(session: Session, file: Any) -> Dict[str, Any]:
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


def bulk_ingest_scans(session: Session, rfid_codes: List[str], reader_name: str | None, batch_id: str | None) -> Dict[str, object]:
    codes = [c.strip() for c in rfid_codes if c and c.strip()]
    if not codes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="rfid_codes must contain at least one non-empty value")

    seen = set()
    unique_codes: List[str] = []
    for code in codes:
        if code not in seen:
            seen.add(code)
            unique_codes.append(code)

    stmt = select(ReaderScan.rfid_code).where(ReaderScan.rfid_code.in_(unique_codes))
    if reader_name is not None:
        stmt = stmt.where(ReaderScan.reader_name == reader_name)
    if batch_id is not None:
        stmt = stmt.where(ReaderScan.batch_id == batch_id)

    existing = {row[0] for row in session.exec(stmt).all()}

    to_create = [
        ReaderScan(rfid_code=code, reader_name=reader_name, batch_id=batch_id)
        for code in unique_codes
        if code not in existing
    ]

    session.add_all(to_create)
    session.commit()

    return {
        "total_received": len(rfid_codes),
        "created_scans": len(to_create),
        "duplicated_codes": sorted(list(existing)),
    }


def detect_scan_anomalies(session: Session) -> Dict[str, object]:
    scans = session.exec(select(ReaderScan).order_by(ReaderScan.scanned_at)).all()

    known_tags = {a.tag_id for a in session.exec(select(Animal)).all()}
    unknown_rfids = sorted({scan.rfid_code for scan in scans if scan.rfid_code not in known_tags})

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

    animal_ids_in_lots = {la.animal_id for la in session.exec(select(LotAnimal)).all()}
    unassigned = []
    for scan in scans:
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
