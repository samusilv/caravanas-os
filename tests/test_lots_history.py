from fastapi.testclient import TestClient

from app.main import app


def test_lot_history_includes_animals_and_events():
    client = TestClient(app)

    # Create animal and lot
    animal = client.post("/animals/", json={"tag_id": "RFID-HIST-LOT", "name": "LotHist"}).json()
    lot = client.post("/lots/", json={"name": "HistoryLot"}).json()

    # Assign animal to lot
    client.post(f"/lots/{lot['id']}/animals/{animal['id']}")

    # Create event for animal
    response = client.post(
        "/events/",
        json={"animal_id": animal['id'], "event_type": "check_out", "notes": "Leaving"},
    )
    assert response.status_code == 201

    response = client.get(f"/lots/{lot['id']}/history")
    assert response.status_code == 200
    data = response.json()

    assert data["lot"]["id"] == lot["id"]
    assert any(a["id"] == animal["id"] for a in data["animals"])
    assert any(e["animal_id"] == animal["id"] for e in data["events"])
