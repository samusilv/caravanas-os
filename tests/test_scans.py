from fastapi.testclient import TestClient

from app.main import app


def test_bulk_scans_creates_and_reports_duplicates():
    client = TestClient(app)

    payload = {
        "rfid_codes": [
            "858123000000001",
            "858123000000002",
        ],
        "reader_name": "manga_reader_1",
        "batch_id": "embarque_001",
    }

    response = client.post("/scans/bulk", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["total_received"] == 2
    assert data["created_scans"] == 2
    assert data["duplicated_codes"] == []

    # Sending again should mark all as duplicates
    response = client.post("/scans/bulk", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["created_scans"] == 0
    assert data["duplicated_codes"] == ["858123000000001", "858123000000002"]


def test_register_scan_creates_single_scan():
    client = TestClient(app)

    payload = {
        "rfid_code": "858123000000099",
        "reader_name": "corral_reader_1",
        "batch_id": "embarque_002",
    }

    response = client.post("/scans", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] is not None
    assert data["rfid_code"] == payload["rfid_code"]
    assert data["reader_name"] == payload["reader_name"]
    assert data["batch_id"] == payload["batch_id"]
    assert data["scanned_at"]


def test_register_scan_requires_rfid_code():
    client = TestClient(app)

    response = client.post(
        "/scans",
        json={"rfid_code": "   ", "reader_name": "corral_reader_1"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "rfid_code is required"
