from fastapi.testclient import TestClient

from app.main import app


def test_create_lot_and_assign_animal():
    client = TestClient(app)

    # Create animal
    animal_payload = {"tag_id": "RFID-9999", "name": "LotTest"}
    animal = client.post("/animals/", json=animal_payload).json()

    # Create lot
    lot_payload = {"name": "Lot A"}
    lot = client.post("/lots/", json=lot_payload).json()

    # Assign animal to lot
    response = client.post(f"/lots/{lot['id']}/animals/{animal['id']}")
    assert response.status_code == 201

    # List animals in lot
    response = client.get(f"/lots/{lot['id']}/animals")
    assert response.status_code == 200
    animals_in_lot = response.json()
    assert any(a["id"] == animal["id"] for a in animals_in_lot)

    # Validate lot
    response = client.get(f"/lots/{lot['id']}/validate")
    assert response.status_code == 200
    data = response.json()
    assert data["expected_count"] == 1
    assert data["scanned_count"] == 0
    assert data["missing_count_estimate"] == 1


def test_assign_from_batch_assigns_and_reports():
    client = TestClient(app)

    # Create animals
    animal1 = client.post("/animals/", json={"tag_id": "RFID-BATCH-1", "name": "A1"}).json()
    animal2 = client.post("/animals/", json={"tag_id": "RFID-BATCH-2", "name": "A2"}).json()

    # Create lot
    lot = client.post("/lots/", json={"name": "BatchLot"}).json()

    # Create scan batch (includes unknown code)
    csv_content = (
        "rfid_code,reader_name,batch_id\n"
        "RFID-BATCH-1,ReaderA,embarque_001\n"
        "RFID-BATCH-2,ReaderA,embarque_001\n"
        "RFID-UNKNOWN,ReaderA,embarque_001\n"
    )
    response = client.post(
        "/imports/scans-csv",
        files={"file": ("scans.csv", csv_content.encode("utf-8"), "text/csv")},
    )
    assert response.status_code == 200

    # Assign from batch
    response = client.post(f"/lots/{lot['id']}/assign-from-batch", json={"batch_id": "embarque_001"})
    assert response.status_code == 200
    data = response.json()

    assert len(data["assigned_animals"]) == 2
    assert {a["tag_id"] for a in data["assigned_animals"]} == {"RFID-BATCH-1", "RFID-BATCH-2"}
    assert all("name" in a for a in data["assigned_animals"])
    assert data["unknown_rfid_codes"] == ["RFID-UNKNOWN"]
    assert data["duplicates"] == []

    # Running again should mark duplicates
    response = client.post(f"/lots/{lot['id']}/assign-from-batch", json={"batch_id": "embarque_001"})
    assert response.status_code == 200
    data = response.json()
    assert set(data["duplicates"]) == {"RFID-BATCH-1", "RFID-BATCH-2"}



def test_validate_lot_returns_detailed_scan_summary():
    client = TestClient(app)

    animal1 = client.post("/animals/", json={"tag_id": "RFID-VAL-A", "name": "A"}).json()
    animal2 = client.post("/animals/", json={"tag_id": "RFID-VAL-B", "name": "B"}).json()
    lot = client.post("/lots/", json={"name": "ValidationDetailedLot"}).json()

    client.post(f"/lots/{lot['id']}/animals/{animal1['id']}")
    client.post(f"/lots/{lot['id']}/animals/{animal2['id']}")

    csv_content = (
        "rfid_code,reader_name,batch_id\n"
        "RFID-VAL-A,ReaderA,VAL-001\n"
        "RFID-VAL-A,ReaderA,VAL-001\n"
        "RFID-UNKNOWN-X,ReaderA,VAL-001\n"
    )
    response = client.post(
        "/imports/scans-csv",
        files={"file": ("scans.csv", csv_content.encode("utf-8"), "text/csv")},
    )
    assert response.status_code == 200

    response = client.get(f"/lots/{lot['id']}/validate")
    assert response.status_code == 200
    data = response.json()

    assert data["expected_count"] == 2
    assert data["scanned_count"] == 1
    assert data["duplicate_rfid_codes"] == ["RFID-VAL-A"]
    assert data["unknown_rfid_codes"] == ["RFID-UNKNOWN-X"]
    assert data["missing_count_estimate"] == 1
    assert "conteo" in data["status_summary"].lower()
