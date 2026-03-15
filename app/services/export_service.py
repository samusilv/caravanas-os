from typing import Dict, List

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models import Animal, Lot, LotAnimal


def get_lot_embarque_rows(session: Session, lot_id: int) -> Dict[str, object]:
    """Return data rows for exporting a lot's embarque report."""
    lot = session.get(Lot, lot_id)
    if not lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lot not found")

    stmt = (
        select(Animal)
        .join(LotAnimal, LotAnimal.animal_id == Animal.id)
        .where(LotAnimal.lot_id == lot_id)
    )

    animals = session.exec(stmt).all()

    rows: List[Dict[str, object]] = [
        {
            "rfid_code": a.tag_id,
            "visual_tag": a.visual_tag or "",
            "category": a.category or "",
            "sex": a.sex or "",
            "estimated_weight_kg": a.estimated_weight or "",
            "lot_name": lot.name,
        }
        for a in animals
    ]

    return {"lot": lot, "rows": rows}
