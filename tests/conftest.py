import pytest

from app.database import init_db


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    """Use a fresh SQLite database file for each test run."""
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    init_db()
    yield
