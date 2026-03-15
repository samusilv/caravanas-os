from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.database import get_session
from app.models import Animal, Lot, LotAnimal, ReaderScan

router = APIRouter(prefix="/lots", tags=["lots"])


@router.post("/", response_model=Lot, status_code=status.HTTP_201_CREATED)
def create_lot(*, session: Session = Depends(get_session), lot: Lot) -> Lot:
    """Create a lot."""
    existing = session.exec(select(Lot).where(Lot.name == lot.name)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lot already exists")

    session.add(lot)
    session.commit()
    session.refresh(lot)
    return lot


@router.get("/", response_model=List[Lot])
def list_lots(*, session: Session = Depends(get_session), limit: int = 100) -> List[Lot]:
    """List existing lots."""
    return session.exec(select(Lot).limit(limit)).all()


@router.post("/{lot_id}/animals/{animal_id}", status_code=status.HTTP_201_CREATED)
def add_animal_to_lot(*, session: Session = Depends(get_session), lot_id: int, animal_id: int) -> dict:
    """Assign an animal to a lot."""
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


@router.get("/{lot_id}/animals", response_model=List[Animal])
def list_animals_in_lot(*, session: Session = Depends(get_session), lot_id: int) -> List[Animal]:
    """List animals assigned to a lot."""
    lot = session.get(Lot, lot_id)
    if not lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lot not found")

    stmt = (
        select(Animal)
        .join(LotAnimal, LotAnimal.animal_id == Animal.id)
        .where(LotAnimal.lot_id == lot_id)
    )
    return session.exec(stmt).all()


@router.get("/{lot_id}/validate")
class AssignFromBatchRequest(BaseModel):
    batch_id: str


@router.post("/{lot_id}/assign-from-batch")
def assign_from_batch(
    *,
    session: Session = Depends(get_session),
    lot_id: int,
    request: AssignFromBatchRequest,
) -> Dict[str, object]:
    """Assign animals to a lot based on a scan batch."""
    lot = session.get(Lot, lot_id)
    if not lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lot not found")

    scans = session.exec(select(ReaderScan).where(ReaderScan.batch_id == request.batch_id)).all()
    codes = [scan.rfid_code for scan in scans]

    if not codes:
        return {"assigned_animals": [], "unknown_rfid_codes": [], "duplicates": []}

    animals = session.exec(select(Animal).where(Animal.tag_id.in_(codes))).all()
    animal_by_tag = {a.tag_id: a for a in animals}

    # Determine existing assignments for the lot
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

        assigned_animals.append({"id": animal.id, "tag_id": animal.tag_id})
        session.add(LotAnimal(lot_id=lot_id, animal_id=animal.id))
        assigned_ids.add(animal.id)

    session.commit()

    return {
        "assigned_animals": assigned_animals,
        "unknown_rfid_codes": unknown_rfid_codes,
        "duplicates": duplicates,
    }


def validate_lot(*, session: Session = Depends(get_session), lot_id: int) -> dict:
    """Validate a lot: returns animal count and whether any animals are missing (example check)."""
    lot = session.get(Lot, lot_id)
    if not lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lot not found")

    animals = session.exec(
        select(Animal)
        .join(LotAnimal, LotAnimal.animal_id == Animal.id)
        .where(LotAnimal.lot_id == lot_id)
    ).all()

    return {
        "lot_id": lot_id,
        "animal_count": len(animals),
        "status": "valid" if animals else "empty",
    }
