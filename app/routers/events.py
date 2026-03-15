from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.models import Event
from app.services.event_service import (
    create_event as service_create_event,
    get_events_for_animal as service_get_events_for_animal,
    list_events as service_list_events,
)

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=Event, status_code=201)
def create_event(*, session: Session = Depends(get_session), event: Event) -> Event:
    """Register an event for an existing animal."""
    return service_create_event(session, event)


@router.get("/", response_model=List[Event])
def list_events(*, session: Session = Depends(get_session), limit: int = 100) -> List[Event]:
    """List recent events."""
    return service_list_events(session, limit)


@router.get("/animal/{animal_id}", response_model=List[Event])
def get_events_for_animal(*, session: Session = Depends(get_session), animal_id: int) -> List[Event]:
    """Get all events for a specific animal."""
    return service_get_events_for_animal(session, animal_id)
