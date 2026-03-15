from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Animal

router = APIRouter(prefix="/animals", tags=["animals"])


@router.post("/", response_model=Animal, status_code=status.HTTP_201_CREATED)
def create_animal(*, session: Session = Depends(get_session), animal: Animal) -> Animal:
    """Register a new animal by its RFID tag."""
    existing = session.exec(select(Animal).where(Animal.tag_id == animal.tag_id)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag already registered")
    session.add(animal)
    session.commit()
    session.refresh(animal)
    return animal


@router.get("/", response_model=List[Animal])
def list_animals(*, session: Session = Depends(get_session), limit: int = 100) -> List[Animal]:
    """List registered animals."""
    return session.exec(select(Animal).limit(limit)).all()


@router.get("/{animal_id}", response_model=Animal)
def get_animal(*, session: Session = Depends(get_session), animal_id: int) -> Animal:
    """Get an animal by ID."""
    animal = session.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Animal not found")
    return animal
