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

### Lots

- `POST /lots/` - create a lot
- `GET /lots/` - list lots
- `POST /lots/{lot_id}/animals/{animal_id}` - assign an animal to a lot
- `GET /lots/{lot_id}/animals` - list animals in a lot
- `GET /lots/{lot_id}/validate` - validate a lot (basic status)

## 🧪 Run tests

```bash
pytest
```
