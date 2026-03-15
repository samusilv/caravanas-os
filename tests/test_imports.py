from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app


def test_import_scans_csv():
    client = TestClient(app)

    csv_content = (
        "rfid_code,reader_name,batch_id\n"
        "ABC123,Reader1,BATCH1\n"
        "DEF456,,BATCH2\n"
        ",,\n"  # empty row (should be skipped)
    )

    response = client.post(
        "/imports/scans-csv",
        files={"file": ("scans.csv", BytesIO(csv_content.encode("utf-8")), "text/csv")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_rows"] == 3
    assert data["imported_rows"] == 2
    assert data["skipped_rows"] == 1
    assert data["errors"] == []


def test_import_scans_csv_requires_rfid_code_column():
    client = TestClient(app)

    csv_content = (
        "reader_name,batch_id\n"
        "Reader1,BATCH1\n"
    )

    response = client.post(
        "/imports/scans-csv",
        files={"file": ("scans.csv", BytesIO(csv_content.encode("utf-8")), "text/csv")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "CSV must contain rfid_code column"
