import os
from functools import lru_cache

from sqlmodel import Session, SQLModel, create_engine


def _get_database_url() -> str:
    """Get the database URL from environment (defaulting to local SQLite)."""
    return os.getenv("DATABASE_URL", "sqlite:///./caravana.db")


@lru_cache
def get_engine():
    """Build and cache the SQLModel engine."""
    return create_engine(_get_database_url(), echo=False)


def init_db() -> None:
    """Create database tables if they do not exist."""
    SQLModel.metadata.create_all(get_engine())


def get_session() -> Session:
    """Get a new database session."""
    return Session(get_engine())
