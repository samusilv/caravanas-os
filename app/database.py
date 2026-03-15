from typing import Optional

from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "sqlite:///./caravana.db"

engine = create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    """Create database tables if they do not exist."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Get a new database session."""
    return Session(engine)
