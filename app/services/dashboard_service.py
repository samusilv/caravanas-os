from datetime import datetime, timedelta

from sqlmodel import Session, select

from app.models import Animal, Event, Lot, ReaderScan


def get_dashboard_summary(session: Session) -> dict:
    """Return a small operational summary for the dashboard."""
    total_animals = session.exec(select(Animal)).count()
    total_lots = session.exec(select(Lot)).count()
    total_scans = session.exec(select(ReaderScan)).count()
    total_events = session.exec(select(Event)).count()

    since = datetime.utcnow() - timedelta(hours=24)
    last_24h_scans = (
        session.exec(select(ReaderScan).where(ReaderScan.scanned_at >= since)).count()
    )

    return {
        "total_animals": total_animals,
        "total_lots": total_lots,
        "total_scans": total_scans,
        "total_events": total_events,
        "last_24h_scans": last_24h_scans,
    }
