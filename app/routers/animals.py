from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_session
from app.models import Animal
from app.services.animal_service import (
    create_animal as service_create_animal,
    get_animal as service_get_animal,
    get_animal_by_rfid as service_get_animal_by_rfid,
    get_animal_history as service_get_animal_history,
    list_animals as service_list_animals,
)

router = APIRouter(prefix="/animals", tags=["animals"])


@router.post("/", response_model=Animal, status_code=status.HTTP_201_CREATED)
def create_animal(*, session: Session = Depends(get_session), animal: Animal) -> Animal:
    """Register a new animal by its RFID tag."""
    return service_create_animal(session, animal)


@router.get("/", response_model=List[Animal])
def list_animals(*, session: Session = Depends(get_session), limit: int = 100) -> List[Animal]:
    """List registered animals."""
    return service_list_animals(session, limit)


@router.get("/by-rfid/{rfid_code}")
def get_animal_by_rfid(*, session: Session = Depends(get_session), rfid_code: str) -> dict:
    """Lookup an animal by RFID and return its event history and current lot."""
    result = service_get_animal_by_rfid(session, rfid_code)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Animal not found")
    return result


@router.get("/{animal_id}", response_model=Animal)
def get_animal(*, session: Session = Depends(get_session), animal_id: int) -> Animal:
    """Get an animal by ID."""
    animal = service_get_animal(session, animal_id)
    if not animal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Animal not found")
    return animal


@router.get("/{animal_id}/history")
def get_animal_history(*, session: Session = Depends(get_session), animal_id: int) -> dict:
    """Get animal info, its events (newest first), and related RFID scans."""
    history = service_get_animal_history(session, animal_id)
    if not history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Animal not found")
    return history
