# CaravanaOS

CaravanaOS is an MVP backend for a livestock RFID tracking platform. It provides an API for reading cattle ear tags, registering events, and validating lots.

## 🚀 Running locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run database migrations:

```bash
alembic upgrade head
```

3. Start the API in development mode:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## ✅ Health check

- `GET /health` - simple status check.

## 📦 API Endpoints (MVP)

All endpoints are available under `/api/v1`. Unprefixed legacy routes are still available temporarily for backward compatibility.

- `GET /api/v1/` - API root
- `POST /api/v1/animals/` - register an animal (requires `tag_id`)
- `GET /api/v1/animals/` - list animals
- `GET /api/v1/animals/{animal_id}` - get animal details
- `POST /api/v1/events/` - create an event for an animal
- `GET /api/v1/events/` - list events
- `GET /api/v1/events/animal/{animal_id}` - list events for an animal
- `GET /api/v1/animals/{animal_id}/history` - get animal info + events (newest first) + scans matched by RFID
- `GET /api/v1/animals/by-rfid/{rfid_code}` - lookup animal by RFID with events (newest first) and current lot
- `POST /api/v1/lots/{lot_id}/assign-from-batch` - assign animals to a lot from a scan batch

assign-from-batch payload:

```json
{
  "batch_id": "embarque_001"
}
```
- `GET /api/v1/lots/{lot_id}/history` - get lot info, animals, and recent events
- `GET /api/v1/exports/lots/{lot_id}/embarque` - download CSV report for lot embarque (`rfid_code`, `visual_tag`, `category`, `sex`, `estimated_weight_kg`, `lot_name`)
- `GET /api/v1/dashboard/summary` - operational dashboard summary
- `POST /api/v1/ai/lot-summary` - generate deterministic Spanish lot-operation summary from validation data
- `GET /api/v1/scans/anomalies` - detect scan anomalies (duplicates, unknown RFIDs, unassigned)
- `POST /api/v1/scans/bulk` - bulk ingest RFID scan codes (JSON payload)
- `POST /api/v1/scans/canonical` - canonical RFID scan ingestion with idempotency key

Example payload:

```json
{
  "rfid_codes": ["858123000000001", "858123000000002"],
  "reader_name": "reader_1",
  "batch_id": "batch_001"
}
```

Canonical ingestion payload:

```json
{
  "device_id": "reader-gate-01",
  "operation_timestamp": "2026-03-15T10:30:00Z",
  "rfid_code": "858123000000001",
  "signal_quality": 0.92,
  "idempotency_key": "reader-gate-01:2026-03-15T10:30:00Z:858123000000001"
}
```

### Lots

- `POST /api/v1/lots/` - create a lot
- `GET /api/v1/lots/` - list lots
- `POST /api/v1/lots/{lot_id}/animals/{animal_id}` - assign an animal to a lot
- `GET /api/v1/lots/{lot_id}/animals` - list animals in a lot
- `GET /api/v1/lots/{lot_id}/validate` - valida lote con resumen de conteo (esperados, escaneados, duplicados, desconocidos)

### CSV import (RFID reader scans)

- `POST /api/v1/imports/scans-csv` - upload a CSV file with columns `rfid_code`, `reader_name` (optional), and `batch_id` (optional).

Example (curl):

```bash
curl -F "file=@scans.csv" http://127.0.0.1:8000/api/v1/imports/scans-csv
```

Response:

- `total_rows`, `imported_rows`, `skipped_rows`, `errors`

Example CSV:

```csv
rfid_code,reader_name,batch_id
ABC123,CorralGate-1,Lote-2026-01
DEF456,,Lote-2026-01
```

## 🧪 Run tests

Run the full test suite using pytest:

```bash
pytest
```

Or run a specific subset of tests:

```bash
pytest tests/test_basic_api.py
```


## 🗃️ Database migrations

- Apply latest migrations:

```bash
alembic upgrade head
```

- Create a new migration after model changes:

```bash
alembic revision --autogenerate -m "describe change"
```

- Roll back one revision:

```bash
alembic downgrade -1
```
