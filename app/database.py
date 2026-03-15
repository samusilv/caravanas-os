import os
from typing import Optional

from sqlmodel import Session, SQLModel, create_engine


def _get_database_url() -> str:
    """Get the database URL from environment (defaulting to local SQLite)."""
    return os.getenv("DATABASE_URL", "sqlite:///./caravana.db")


def _get_engine():
    return create_engine(_get_database_url(), echo=False)


def init_db() -> None:
    """Create database tables if they do not exist."""
    engine = _get_engine()
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Get a new database session."""
    engine = _get_engine()
    return Session(engine)
