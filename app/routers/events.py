from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Animal, Event, EventType

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=Event, status_code=status.HTTP_201_CREATED)
def create_event(*, session: Session = Depends(get_session), event: Event) -> Event:
    """Register an event for an existing animal."""
    animal = session.get(Animal, event.animal_id)
    if not animal:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Animal not found")

    # Normalize event timestamps to UTC
    event.recorded_at = event.recorded_at or datetime.utcnow()

    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.get("/", response_model=List[Event])
def list_events(*, session: Session = Depends(get_session), limit: int = 100) -> List[Event]:
    """List recent events."""
    return session.exec(select(Event).limit(limit)).all()


@router.get("/animal/{animal_id}", response_model=List[Event])
def get_events_for_animal(*, session: Session = Depends(get_session), animal_id: int) -> List[Event]:
    """Get all events for a specific animal."""
    return session.exec(select(Event).where(Event.animal_id == animal_id)).all()
