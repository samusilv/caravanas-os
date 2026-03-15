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
    assert response.json()["status"] == "valid"


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
        "RFID-BATCH-1,ReaderA,BATCH123\n"
        "RFID-BATCH-2,ReaderA,BATCH123\n"
        "RFID-UNKNOWN,ReaderA,BATCH123\n"
    )
    response = client.post(
        "/imports/scans-csv",
        files={"file": ("scans.csv", csv_content.encode("utf-8"), "text/csv")},
    )
    assert response.status_code == 200

    # Assign from batch
    response = client.post(f"/lots/{lot['id']}/assign-from-batch", json={"batch_id": "BATCH123"})
    assert response.status_code == 200
    data = response.json()

    assert len(data["assigned_animals"]) == 2
    assert data["unknown_rfid_codes"] == ["RFID-UNKNOWN"]
    assert data["duplicates"] == []

    # Running again should mark duplicates
    response = client.post(f"/lots/{lot['id']}/assign-from-batch", json={"batch_id": "BATCH123"})
    assert response.status_code == 200
    data = response.json()
    assert set(data["duplicates"]) == {"RFID-BATCH-1", "RFID-BATCH-2"}
