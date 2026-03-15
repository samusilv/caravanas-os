from io import BytesIO

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


def test_animal_history_includes_events_and_scans():
    client = TestClient(app)

    # Create animal
    response = client.post("/animals/", json={"tag_id": "RFID-HIST", "name": "History"})
    assert response.status_code == 201
    animal = response.json()

    # Create an event
    response = client.post(
        "/events/",
        json={
            "animal_id": animal["id"],
            "event_type": "check_in",
            "notes": "History test",
        },
    )
    assert response.status_code == 201

    # Create a scan matching the tag
    response = client.post(
        "/imports/scans-csv",
        files={
            "file": (
                "scans.csv",
                BytesIO(b"rfid_code,reader_name,batch_id\nRFID-HIST,Scanner,TEST\n"),
                "text/csv",
            )
        },
    )
    assert response.status_code == 200

    # Fetch history
    response = client.get(f"/animals/{animal['id']}/history")
    assert response.status_code == 200
    history = response.json()

    assert history["animal"]["id"] == animal["id"]
    assert len(history["events"]) == 1
    assert len(history["scans"]) == 1
    assert history["scans"][0]["rfid_code"] == "RFID-HIST"


def test_lookup_by_rfid_includes_events_and_current_lot():
    client = TestClient(app)

    # Create animal
    response = client.post("/animals/", json={"tag_id": "RFID-LOOKUP", "name": "Lookup"})
    assert response.status_code == 201
    animal = response.json()

    # Create a lot and assign animal
    response = client.post("/lots/", json={"name": "LotX"})
    assert response.status_code == 201
    lot = response.json()

    response = client.post(f"/lots/{lot['id']}/animals/{animal['id']}")
    assert response.status_code == 201

    # Create an event
    response = client.post(
        "/events/",
        json={
            "animal_id": animal["id"],
            "event_type": "movement",
            "notes": "Moved to LotX",
        },
    )
    assert response.status_code == 201

    # Lookup by RFID
    response = client.get(f"/animals/by-rfid/{animal['tag_id']}")
    assert response.status_code == 200
    data = response.json()

    assert data["animal"]["id"] == animal["id"]
    assert len(data["events"]) == 1
    assert data["current_lot"]["id"] == lot["id"]
