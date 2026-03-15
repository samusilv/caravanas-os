from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class EventType(str, Enum):
    check_in = "check_in"
    check_out = "check_out"
    movement = "movement"


class Animal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tag_id: str = Field(index=True)
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    animal_id: int = Field(foreign_key="animal.id")
    event_type: EventType
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
