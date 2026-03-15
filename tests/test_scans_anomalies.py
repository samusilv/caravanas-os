from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.database import get_session
from app.main import app
from app.models import ReaderScan


def test_scan_anomalies_detection():
    client = TestClient(app)

    # Create a known animal
    response = client.post("/animals/", json={"tag_id": "RFID-ANOM", "name": "Anom"})
    assert response.status_code == 201

    # Insert scans manually to create anomalies
    now = datetime.utcnow()
    with get_session() as session:
        session.add_all(
            [
                ReaderScan(rfid_code="RFID-ANOM", scanned_at=now - timedelta(minutes=4)),
                ReaderScan(rfid_code="RFID-ANOM", scanned_at=now - timedelta(minutes=2)),
                ReaderScan(rfid_code="RFID-ANOM", scanned_at=now),
                ReaderScan(rfid_code="RFID-UNKNOWN", scanned_at=now),
            ]
        )
        session.commit()

    response = client.get("/scans/anomalies")
    assert response.status_code == 200
    data = response.json()

    assert "unknown_rfids" in data
    assert "RFID-UNKNOWN" in data["unknown_rfids"]
    assert "multiple_quick_scans" in data
    assert any(item["rfid_code"] == "RFID-ANOM" for item in data["multiple_quick_scans"])
    assert "unassigned_scans" in data
    assert any(item["rfid_code"] == "RFID-ANOM" for item in data["unassigned_scans"])
