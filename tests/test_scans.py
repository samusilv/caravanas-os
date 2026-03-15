from fastapi.testclient import TestClient

from app.main import app


def test_bulk_scans_creates_and_dedupes():
    client = TestClient(app)

    payload = {
        "rfid_codes": [
            "858123000000001",
            "858123000000002",
            "858123000000001",  # duplicate in request
        ],
        "reader_name": "manga_reader_1",
        "batch_id": "embarque_001",
    }

    response = client.post("/scans/bulk", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["total_received"] == 3
    assert data["created_scans"] == 2
    assert data["duplicated_codes"] == ["858123000000001"]

    # Sending again should mark all as duplicates
    response = client.post("/scans/bulk", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["created_scans"] == 0
    assert set(data["duplicated_codes"]) == {"858123000000001", "858123000000002"}
