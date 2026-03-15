from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Animal, Lot, LotAnimal

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
