from datetime import datetime, timedelta

from sqlalchemy import func
from sqlmodel import Session, select

from app.infrastructure.db.models import Animal, Event, Lot, ReaderScan


def _count_rows(session: Session, model) -> int:
    return int(session.exec(select(func.count()).select_from(model)).one())


def get_dashboard_summary(session: Session) -> dict:
    total_animals = _count_rows(session, Animal)
    total_lots = _count_rows(session, Lot)
    total_scans = _count_rows(session, ReaderScan)
    total_events = _count_rows(session, Event)

    since = datetime.utcnow() - timedelta(hours=24)
    last_24h_scans = int(
        session.exec(
            select(func.count())
            .select_from(ReaderScan)
            .where(ReaderScan.scanned_at >= since)
        ).one()
    )

    return {
        "total_animals": total_animals,
        "total_lots": total_lots,
        "total_scans": total_scans,
        "total_events": total_events,
        "last_24h_scans": last_24h_scans,
    }
