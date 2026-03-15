import csv
from io import StringIO
from typing import Generator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from app.infrastructure.db.session import get_session
from app.application.services.export_service import get_lot_embarque_rows

router = APIRouter(prefix="/exports", tags=["exports"])


def _generate_csv(rows: list[dict]) -> Generator[str, None, None]:
    buffer = StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=[
            "rfid_code",
            "visual_tag",
            "category",
            "sex",
            "estimated_weight_kg",
            "lot_name",
        ],
    )
    writer.writeheader()
    yield buffer.getvalue()
    buffer.seek(0)
    buffer.truncate(0)

    for row in rows:
        writer.writerow(row)
        yield buffer.getvalue()
        buffer.seek(0)
        buffer.truncate(0)


@router.get("/lots/{lot_id}/embarque")
def export_lot_embarque(*, session: Session = Depends(get_session), lot_id: int):
    """Export lot contents to a CSV suitable for embarque reporting."""
    result = get_lot_embarque_rows(session, lot_id)

    filename = f"lot_{lot_id}_embarque.csv"
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return StreamingResponse(
        _generate_csv(result["rows"]), media_type="text/csv", headers=headers
    )
