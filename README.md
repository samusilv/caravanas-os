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
