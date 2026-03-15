from typing import Dict, List

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.infrastructure.db.models import Animal, Event, ReaderScan


def create_animal(session: Session, animal: Animal) -> Animal:
    existing = session.exec(select(Animal).where(Animal.tag_id == animal.tag_id)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag already registered")

    session.add(animal)
    session.commit()
    session.refresh(animal)
    return animal


def list_animals(session: Session, limit: int = 100) -> List[Animal]:
    return session.exec(select(Animal).limit(limit)).all()


def get_animal(session: Session, animal_id: int) -> Animal | None:
    return session.get(Animal, animal_id)


def get_animal_history(session: Session, animal_id: int) -> Dict[str, object]:
    animal = get_animal(session, animal_id)
    if not animal:
        return {}

    events = (
        session.exec(
            select(Event)
            .where(Event.animal_id == animal_id)
            .order_by(Event.recorded_at.desc())
        )
        .all()
    )

    scans = (
        session.exec(
            select(ReaderScan)
            .where(ReaderScan.rfid_code == animal.tag_id)
            .order_by(ReaderScan.scanned_at.desc())
        )
        .all()
    )

    return {
        "animal": animal,
        "events": events,
        "scans": scans,
    }


def get_animal_by_rfid(session: Session, rfid_code: str) -> Dict[str, object]:
    animal = session.exec(select(Animal).where(Animal.tag_id == rfid_code)).first()
    if not animal:
        return {}

    events = (
        session.exec(
            select(Event)
            .where(Event.animal_id == animal.id)
            .order_by(Event.recorded_at.desc())
        )
        .all()
    )

    from app.infrastructure.db.models import Lot, LotAnimal

    last_lot = (
        session.exec(
            select(Lot)
            .join(LotAnimal, LotAnimal.lot_id == Lot.id)
            .where(LotAnimal.animal_id == animal.id)
            .order_by(Lot.created_at.desc())
            .limit(1)
        )
        .first()
    )

    return {
        "animal": animal,
        "events": events,
        "current_lot": last_lot,
        "last_lot": last_lot,
    }
