from typing import Dict, List

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models import Animal, Event, Lot, LotAnimal, ReaderScan


def create_lot(session: Session, lot: Lot) -> Lot:
    existing = session.exec(select(Lot).where(Lot.name == lot.name)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lot already exists")

    session.add(lot)
    session.commit()
    session.refresh(lot)
    return lot


def list_lots(session: Session, limit: int = 100) -> List[Lot]:
    return session.exec(select(Lot).limit(limit)).all()


def add_animal_to_lot(session: Session, lot_id: int, animal_id: int) -> Dict[str, int]:
    lot = session.get(Lot, lot_id)
    if not lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lot not found")
    animal = session.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Animal not found")

    exists = session.get(LotAnimal, (lot_id, animal_id))
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Animal already in lot")

    association = LotAnimal(lot_id=lot_id, animal_id=animal_id)
    session.add(association)
    session.commit()
    return {"lot_id": lot_id, "animal_id": animal_id}


def list_animals_in_lot(session: Session, lot_id: int) -> List[Animal]:
    lot = session.get(Lot, lot_id)
    if not lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lot not found")

    stmt = (
        select(Animal)
        .join(LotAnimal, LotAnimal.animal_id == Animal.id)
        .where(LotAnimal.lot_id == lot_id)
    )
    return session.exec(stmt).all()


def validate_lot(session: Session, lot_id: int) -> Dict[str, object]:
    lot = session.get(Lot, lot_id)
    if not lot:
        return {}

    animals = session.exec(
        select(Animal)
        .join(LotAnimal, LotAnimal.animal_id == Animal.id)
        .where(LotAnimal.lot_id == lot_id)
    ).all()

    expected_count = len(animals)
    lot_tags = {animal.tag_id for animal in animals if animal.tag_id}

    if not lot_tags:
        return {
            "expected_count": 0,
            "scanned_count": 0,
            "duplicate_rfid_codes": [],
            "unknown_rfid_codes": [],
            "missing_count_estimate": 0,
            "status_summary": "Lote vacío: no hay animales asignados.",
        }

    scan_codes = [scan.rfid_code for scan in session.exec(select(ReaderScan)).all() if scan.rfid_code]
    known_tags = {animal.tag_id for animal in session.exec(select(Animal)).all() if animal.tag_id}

    lot_scan_counts: Dict[str, int] = {}
    for code in scan_codes:
        if code in lot_tags:
            lot_scan_counts[code] = lot_scan_counts.get(code, 0) + 1

    scanned_count = len(set(lot_scan_counts.keys()))
    duplicate_rfid_codes = sorted([code for code, count in lot_scan_counts.items() if count > 1])
    unknown_rfid_codes = sorted({code for code in scan_codes if code not in known_tags})
    missing_count_estimate = max(expected_count - scanned_count, 0)

    if missing_count_estimate == 0 and not duplicate_rfid_codes and not unknown_rfid_codes:
        status_summary = "Validación OK: conteo completo y sin anomalías."
    elif missing_count_estimate == 0:
        status_summary = "Conteo completo, con observaciones de duplicados o RFIDs desconocidos."
    else:
        status_summary = f"Conteo incompleto: faltan {missing_count_estimate} animales por escanear."

    return {
        "expected_count": expected_count,
        "scanned_count": scanned_count,
        "duplicate_rfid_codes": duplicate_rfid_codes,
        "unknown_rfid_codes": unknown_rfid_codes,
        "missing_count_estimate": missing_count_estimate,
        "status_summary": status_summary,
    }


def lot_history(session: Session, lot_id: int) -> Dict[str, object]:
    lot = session.get(Lot, lot_id)
    if not lot:
        return {}

    animals = session.exec(
        select(Animal)
        .join(LotAnimal, LotAnimal.animal_id == Animal.id)
        .where(LotAnimal.lot_id == lot_id)
    ).all()

    animal_ids = [a.id for a in animals]
    events = (
        session.exec(
            select(Event)
            .where(Event.animal_id.in_(animal_ids))
            .order_by(Event.recorded_at.desc())
        )
        .all()
    )

    return {
        "lot": lot,
        "animals": animals,
        "events": events,
    }


def assign_from_batch(session: Session, lot_id: int, batch_id: str) -> Dict[str, object]:
    lot = session.get(Lot, lot_id)
    if not lot:
        return {}

    scans = session.exec(select(ReaderScan).where(ReaderScan.batch_id == batch_id)).all()
    codes = [scan.rfid_code for scan in scans if scan.rfid_code]

    if not codes:
        return {"assigned_animals": [], "unknown_rfid_codes": [], "duplicates": []}

    unique_codes = list(dict.fromkeys(codes))
    animals = session.exec(select(Animal).where(Animal.tag_id.in_(unique_codes))).all()
    animal_by_tag = {a.tag_id: a for a in animals}

    assigned = session.exec(
        select(LotAnimal).where(
            LotAnimal.lot_id == lot_id,
            LotAnimal.animal_id.in_([a.id for a in animals]),
        )
    ).all()
    assigned_ids = {a.animal_id for a in assigned}

    assigned_animals = []
    duplicates: List[str] = []
    unknown_rfid_codes: List[str] = []

    for code in codes:
        animal = animal_by_tag.get(code)
        if not animal:
            if code not in unknown_rfid_codes:
                unknown_rfid_codes.append(code)
            continue

        if animal.id in assigned_ids:
            if code not in duplicates:
                duplicates.append(code)
            continue

        assigned_animals.append({"id": animal.id, "tag_id": animal.tag_id, "name": animal.name})
        session.add(LotAnimal(lot_id=lot_id, animal_id=animal.id))
        assigned_ids.add(animal.id)

    if assigned_animals:
        session.commit()

    return {
        "assigned_animals": assigned_animals,
        "unknown_rfid_codes": unknown_rfid_codes,
        "duplicates": duplicates,
    }
