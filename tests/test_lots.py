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
