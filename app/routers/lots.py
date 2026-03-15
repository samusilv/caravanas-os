from typing import Dict, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from app.database import get_session
from app.models import Animal, Lot
from app.services.lot_service import (
    add_animal_to_lot as service_add_animal_to_lot,
    assign_from_batch as service_assign_from_batch,
    create_lot as service_create_lot,
    list_lots as service_list_lots,
    list_animals_in_lot as service_list_animals_in_lot,
    lot_history as service_lot_history,
    validate_lot as service_validate_lot,
)

router = APIRouter(prefix="/lots", tags=["lots"])


@router.post("/", response_model=Lot, status_code=201)
def create_lot(*, session: Session = Depends(get_session), lot: Lot) -> Lot:
    """Create a lot."""
    return service_create_lot(session, lot)


@router.get("/", response_model=List[Lot])
def list_lots(*, session: Session = Depends(get_session), limit: int = 100) -> List[Lot]:
    """List existing lots."""
    return service_list_lots(session, limit)


@router.post("/{lot_id}/animals/{animal_id}", status_code=201)
def add_animal_to_lot(*, session: Session = Depends(get_session), lot_id: int, animal_id: int) -> dict:
    """Assign an animal to a lot."""
    return service_add_animal_to_lot(session, lot_id, animal_id)


@router.get("/{lot_id}/animals", response_model=List[Animal])
def list_animals_in_lot(*, session: Session = Depends(get_session), lot_id: int) -> List[Animal]:
    """List animals assigned to a lot."""
    return service_list_animals_in_lot(session, lot_id)


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
    result = service_assign_from_batch(session, lot_id, request.batch_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lot not found")
    return result


@router.get("/{lot_id}/history")
def lot_history(*, session: Session = Depends(get_session), lot_id: int) -> dict:
    """Return lot info, animals assigned, and recent events for the lot."""
    result = service_lot_history(session, lot_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lot not found")
    return result


@router.get("/{lot_id}/validate")
def validate_lot(*, session: Session = Depends(get_session), lot_id: int) -> dict:
    """Validate a lot: returns animal count and whether any animals are missing (example check)."""
    result = service_validate_lot(session, lot_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lot not found")
    return result
