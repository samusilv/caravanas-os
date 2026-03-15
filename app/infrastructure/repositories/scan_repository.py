import csv
from datetime import timedelta
from io import TextIOWrapper
from typing import Any, Dict, List

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.infrastructure.db.models import Animal, LotAnimal, ReaderScan


def import_scans_csv(session: Session, file: Any) -> Dict[str, Any]:
    if file.content_type not in ("text/csv", "application/vnd.ms-excel", "text/plain"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a CSV")

    decoded = TextIOWrapper(file.file, encoding="utf-8-sig", newline="")
    reader = csv.DictReader(decoded)

    if not reader.fieldnames or "rfid_code" not in reader.fieldnames:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CSV must contain rfid_code column")

    total_rows = 0
    imported_rows = 0
    skipped_rows = 0
    errors: List[Dict[str, Any]] = []
    scans_to_create: List[ReaderScan] = []

    for row_num, row in enumerate(reader, start=1):
        total_rows += 1

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

        scans_to_create.append(ReaderScan(rfid_code=rfid_code, reader_name=reader_name, batch_id=batch_id))

    if scans_to_create:
        session.add_all(scans_to_create)
        session.commit()
        imported_rows = len(scans_to_create)

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

    input_codes = set(codes)
    stmt = select(ReaderScan.rfid_code).where(ReaderScan.rfid_code.in_(input_codes))
    if reader_name is not None:
        stmt = stmt.where(ReaderScan.reader_name == reader_name)
    if batch_id is not None:
        stmt = stmt.where(ReaderScan.batch_id == batch_id)

    existing = set(session.exec(stmt).all())

    to_create = [
        ReaderScan(rfid_code=code, reader_name=reader_name, batch_id=batch_id)
        for code in codes
        if code not in existing
    ]

    if to_create:
        session.add_all(to_create)
        session.commit()

    return {
        "total_received": len(rfid_codes),
        "created_scans": len(to_create),
        "duplicated_codes": sorted(existing),
    }


def create_scan(session: Session, rfid_code: str, reader_name: str | None, batch_id: str | None) -> ReaderScan:
    code = rfid_code.strip()
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="rfid_code is required")

    scan = ReaderScan(rfid_code=code, reader_name=reader_name, batch_id=batch_id)
    session.add(scan)
    session.commit()
    session.refresh(scan)
    return scan


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
