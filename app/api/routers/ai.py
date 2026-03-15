from typing import Dict

from fastapi import APIRouter

from app.ai.operation_summary import summarize_lot_validation
from app.schemas import LotSummaryRequest

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/lot-summary")
def lot_summary(request: LotSummaryRequest) -> Dict[str, str]:
    """Return a deterministic Spanish summary for lot validation results."""
    summary = summarize_lot_validation(
        scanned_count=request.scanned_count,
        unknown_count=len(request.unknown_rfid_codes),
        duplicate_count=len(request.duplicate_rfid_codes),
        missing_count=request.missing_count_estimate,
    )
    return {"summary": summary}
