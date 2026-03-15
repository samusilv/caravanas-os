from fastapi.testclient import TestClient

from app.main import app


def test_create_and_get_animal():
    client = TestClient(app)

    # Create
    payload = {"tag_id": "RFID-1234", "name": "Bessie"}
    response = client.post("/animals/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["tag_id"] == "RFID-1234"
    assert data["name"] == "Bessie"

    animal_id = data["id"]

    # Get
    response = client.get(f"/animals/{animal_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == animal_id
    assert data["tag_id"] == "RFID-1234"
