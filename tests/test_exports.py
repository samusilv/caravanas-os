from fastapi.testclient import TestClient

from app.main import app


def test_export_lot_embarque_csv():
    client = TestClient(app)

    # Create animal with extra fields
    animal = client.post(
        "/animals/",
        json={
            "tag_id": "RFID-EXP-1",
            "name": "Export",
            "visual_tag": "V-123",
            "category": "Cattle",
            "sex": "F",
            "estimated_weight": 320.5,
        },
    ).json()

    # Create lot and assign animal
    lot = client.post("/lots/", json={"name": "ExportLot"}).json()
    client.post(f"/lots/{lot['id']}/animals/{animal['id']}")

    response = client.get(f"/exports/lots/{lot['id']}/embarque")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment; filename=lot_" in response.headers["content-disposition"]

    text = response.text
    assert "rfid_code" in text
    assert "V-123" in text
    assert "ExportLot" in text
