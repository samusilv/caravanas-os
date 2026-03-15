from fastapi.testclient import TestClient

from app.main import app


def test_create_animal_endpoint():
    client = TestClient(app)

    payload = {"tag_id": "RFID-TEST-1", "name": "Test Animal"}
    response = client.post("/animals/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["tag_id"] == payload["tag_id"]
    assert data["name"] == payload["name"]


def test_create_lot_endpoint():
    client = TestClient(app)

    payload = {"name": "Test Lot"}
    response = client.post("/lots/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == payload["name"]


def test_bulk_scans_endpoint():
    client = TestClient(app)

    payload = {
        "rfid_codes": ["858123000000001", "858123000000002"],
        "reader_name": "reader_1",
        "batch_id": "batch_001",
    }

    response = client.post("/scans/bulk", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["total_received"] == 2
    assert data["created_scans"] == 2
    assert data["duplicated_codes"] == []


def test_lot_validation_endpoint():
    client = TestClient(app)

    # Create lot
    lot = client.post("/lots/", json={"name": "Validation Lot"}).json()

    # Validate empty lot
    response = client.get(f"/lots/{lot['id']}/validate")
    assert response.status_code == 200
    data = response.json()
    assert data["expected_count"] == 0
    assert data["scanned_count"] == 0
    assert data["missing_count_estimate"] == 0
    assert "status_summary" in data

    # Create animal and assign to lot
    animal = client.post("/animals/", json={"tag_id": "RFID-VAL-1", "name": "Val"}).json()
    client.post(f"/lots/{lot['id']}/animals/{animal['id']}")

    response = client.get(f"/lots/{lot['id']}/validate")
    assert response.status_code == 200
    data = response.json()
    assert data["expected_count"] == 1
    assert data["scanned_count"] == 0
    assert data["missing_count_estimate"] == 1
    assert "incompleto" in data["status_summary"].lower()
