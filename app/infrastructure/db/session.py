import os
from functools import lru_cache
from pathlib import Path

from sqlmodel import Session, create_engine


def _get_database_url() -> str:
    """Get the database URL from environment (defaulting to local SQLite)."""
    return os.getenv("DATABASE_URL", "sqlite:///./caravana.db")


@lru_cache
def get_engine():
    """Build and cache the SQLModel engine."""
    return create_engine(_get_database_url(), echo=False)


def _alembic_config():
    from alembic.config import Config

    project_root = Path(__file__).resolve().parents[3]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", _get_database_url())
    return config


def init_db() -> None:
    """Apply database migrations up to the latest revision."""
    try:
        from alembic import command
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Alembic is required to initialize the database. Install dependencies with `pip install -r requirements.txt`."
        ) from exc

    command.upgrade(_alembic_config(), "head")


def get_session() -> Session:
    """Get a new database session."""
    return Session(get_engine())
