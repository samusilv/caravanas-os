from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Index
from sqlmodel import Field, SQLModel


class EventType(str, Enum):
    check_in = "check_in"
    check_out = "check_out"
    movement = "movement"


class Animal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tag_id: str = Field(index=True, unique=True)
    name: Optional[str] = None
    visual_tag: Optional[str] = None
    category: Optional[str] = None
    sex: Optional[str] = None
    estimated_weight: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)


class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    animal_id: int = Field(foreign_key="animal.id")
    event_type: EventType
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)


class Lot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)


class LotAnimal(SQLModel, table=True):
    lot_id: int = Field(foreign_key="lot.id", primary_key=True)
    animal_id: int = Field(foreign_key="animal.id", primary_key=True)


class ReaderScan(SQLModel, table=True):
    __table_args__ = (
        Index("ix_readerscan_rfid_code_batch_id_scanned_at", "rfid_code", "batch_id", "scanned_at"),
        Index("ix_readerscan_idempotency_key", "idempotency_key", unique=True),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    rfid_code: str = Field(index=True)
    reader_name: Optional[str] = None
    batch_id: Optional[str] = None
    device_id: Optional[str] = None
    signal_quality: Optional[float] = None
    idempotency_key: Optional[str] = None
    scanned_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)
