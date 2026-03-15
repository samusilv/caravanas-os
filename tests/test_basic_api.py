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
        "rfid_codes": ["RFID-B1", "RFID-B2", "RFID-B1"],
        "reader_name": "test_reader",
        "batch_id": "BATCH-123",
    }

    response = client.post("/scans/bulk", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["total_received"] == 3
    assert data["created_scans"] == 2
    assert data["duplicated_codes"] == ["RFID-B1"]


def test_lot_validation_endpoint():
    client = TestClient(app)

    # Create lot
    lot = client.post("/lots/", json={"name": "Validation Lot"}).json()

    # Validate empty lot
    response = client.get(f"/lots/{lot['id']}/validate")
    assert response.status_code == 200
    assert response.json()["status"] == "empty"

    # Create animal and assign to lot
    animal = client.post("/animals/", json={"tag_id": "RFID-VAL-1", "name": "Val"}).json()
    client.post(f"/lots/{lot['id']}/animals/{animal['id']}")

    response = client.get(f"/lots/{lot['id']}/validate")
    assert response.status_code == 200
    assert response.json()["status"] == "valid"
