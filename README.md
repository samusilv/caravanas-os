# CaravanaOS

CaravanaOS is an MVP backend for a livestock RFID tracking platform. It provides an API for reading cattle ear tags, registering events, and validating lots.

## 🚀 Running locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the API in development mode:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## ✅ Health check

- `GET /health` - simple status check.

## 📦 API Endpoints (MVP)

- `GET /` - API root
- `POST /animals/` - register an animal (requires `tag_id`)
- `GET /animals/` - list animals
- `GET /animals/{animal_id}` - get animal details
- `POST /events/` - create an event for an animal
- `GET /events/` - list events
- `GET /events/animal/{animal_id}` - list events for an animal
- `GET /animals/{animal_id}/history` - get animal info + events + scans
- `GET /animals/by-rfid/{rfid_code}` - lookup animal by RFID with events and last known lot
- `POST /lots/{lot_id}/assign-from-batch` - assign animals to a lot from a scan batch
- `POST /scans/bulk` - bulk ingest RFID scan codes (JSON payload)

### Lots

- `POST /lots/` - create a lot
- `GET /lots/` - list lots
- `POST /lots/{lot_id}/animals/{animal_id}` - assign an animal to a lot
- `GET /lots/{lot_id}/animals` - list animals in a lot
- `GET /lots/{lot_id}/validate` - validate a lot (basic status)

### CSV import (RFID reader scans)

- `POST /imports/scans-csv` - upload a CSV file with columns `rfid_code`, `reader_name` (optional), and `batch_id` (optional).

Example (curl):

```bash
curl -F "file=@scans.csv" http://127.0.0.1:8000/imports/scans-csv
```

Response:

- `total_rows`, `imported_rows`, `skipped_rows`, `errors`

## 🧪 Run tests

```bash
pytest
```
