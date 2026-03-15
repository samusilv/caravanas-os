from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class BulkScanRequest(BaseModel):
    rfid_codes: List[str]
    reader_name: Optional[str] = None
    batch_id: Optional[str] = None


class ScanCreateRequest(BaseModel):
    rfid_code: str
    reader_name: Optional[str] = None
    batch_id: Optional[str] = None


class CanonicalScanIngestRequest(BaseModel):
    device_id: str
    operation_timestamp: datetime
    rfid_code: str
    signal_quality: float
    idempotency_key: str


class AssignFromBatchRequest(BaseModel):
    batch_id: str


class LotSummaryRequest(BaseModel):
    expected_count: int
    scanned_count: int
    duplicate_rfid_codes: List[str]
    unknown_rfid_codes: List[str]
    missing_count_estimate: int
    status_summary: str
