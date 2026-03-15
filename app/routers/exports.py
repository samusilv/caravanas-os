import csv
from io import StringIO
from typing import Generator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from app.database import get_session
from app.models import Animal, Lot, LotAnimal

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
            "estimated_weight",
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
    lot = session.get(Lot, lot_id)
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")

    stmt = (
        select(Animal)
        .join(LotAnimal, LotAnimal.animal_id == Animal.id)
        .where(LotAnimal.lot_id == lot_id)
    )

    animals = session.exec(stmt).all()

    rows = [
        {
            "rfid_code": a.tag_id,
            "visual_tag": a.visual_tag or "",
            "category": a.category or "",
            "sex": a.sex or "",
            "estimated_weight": a.estimated_weight or "",
            "lot_name": lot.name,
        }
        for a in animals
    ]

    filename = f"lot_{lot_id}_embarque.csv"
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return StreamingResponse(
        _generate_csv(rows), media_type="text/csv", headers=headers
    )
