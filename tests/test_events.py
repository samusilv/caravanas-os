from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app


def test_create_event_for_animal():
    client = TestClient(app)

    # Ensure animal exists
    payload = {"tag_id": "RFID-5678", "name": "Moo"
              }
    response = client.post("/animals/", json=payload)
    assert response.status_code == 201
    animal_id = response.json()["id"]

    # Create event
    event_payload = {
        "animal_id": animal_id,
        "event_type": "check_in",
        "notes": "Arrived at farm",
    }
    response = client.post("/events/", json=event_payload)
    assert response.status_code == 201
    event = response.json()
    assert event["animal_id"] == animal_id
    assert event["event_type"] == "check_in"

    # Fetch events for animal
    response = client.get(f"/events/animal/{animal_id}")
    assert response.status_code == 200
    events = response.json()
    assert any(e["id"] == event["id"] for e in events)
