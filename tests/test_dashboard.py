from fastapi.testclient import TestClient

from app.main import app


def test_dashboard_summary_counts():
    client = TestClient(app)

    # create some data
    client.post("/animals/", json={"tag_id": "RFID-DASH-1", "name": "D1"})
    client.post("/lots/", json={"name": "DashLot"})
    client.post(
        "/imports/scans-csv",
        files={
            "file": (
                "scans.csv",
                b"rfid_code,reader_name,batch_id\nRFID-DASH-1,ReaderX,DASH01\n",
                "text/csv",
            )
        },
    )
    client.post(
        "/events/",
        json={"animal_id": 1, "event_type": "check_in", "notes": "dash"},
    )

    response = client.get("/dashboard/summary")
    assert response.status_code == 200
    data = response.json()

    assert data["total_animals"] >= 1
    assert data["total_lots"] >= 1
    assert data["total_scans"] >= 1
    assert data["total_events"] >= 1
    assert "last_24h_scans" in data
