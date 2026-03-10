# PayDay Express DR – WhatsApp Bot

A professional-grade WhatsApp chatbot built with **FastAPI** and **Twilio**, designed to handle loan-related customer interactions for PayDay Express DR.

## Features

- **Inbound message handling** via a Twilio webhook with a guided menu (FAQ, loan status, contact)
- **Conversation state machine** that tracks each user's position in the chat flow
- **FAQ system** with pre-built answers for the most common questions
- **Loan status lookup** (stub; plug in your loan-management database)
- **Proactive push notifications** – a dedicated REST endpoint lets external systems send WhatsApp messages to users when their loan status changes
- **Async throughout** – all I/O uses `async`/`await` (SQLAlchemy, httpx)
- **SQLite by default** (development); drop-in for PostgreSQL / MySQL in production

---

## Project Structure

```
paydayexpressdr-bot/
├── main.py                  # FastAPI app, lifespan, global exception handler
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Test/dev dependencies
├── pytest.ini               # Pytest configuration
├── .env.example             # Environment variable template
├── routers/
│   ├── webhook.py           # POST /webhook/twilio  – inbound message handler
│   └── notifications.py     # POST /notifications/push – outbound push endpoint
├── services/
│   ├── message_parser.py    # Conversation state machine & FAQ logic
│   ├── state_manager.py     # In-memory + DB state cache
│   └── twilio_service.py    # Async Twilio REST API client
├── models/
│   ├── webhook.py           # Pydantic schemas for Twilio webhook payload
│   └── notification.py      # Pydantic schemas for push-notification request/response
├── database/
│   ├── config.py            # Pydantic-settings (loads .env)
│   ├── connection.py        # SQLAlchemy async engine & session factory
│   └── orm_models.py        # ORM models: UserState, MessageLog
└── tests/
    ├── conftest.py          # Shared fixtures (in-memory DB, test client)
    ├── test_webhook.py      # Tests for the webhook endpoint
    └── test_notifications.py# Tests for the push-notification endpoint
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|---|---|---|
| `TWILIO_ACCOUNT_SID` | Twilio Account SID (starts with `AC`) | *(required)* |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | *(required)* |
| `TWILIO_WHATSAPP_FROM` | Your Twilio WhatsApp sandbox/sender number with `whatsapp:` prefix | `whatsapp:+14155238886` |
| `DATABASE_URL` | SQLAlchemy async connection string | `sqlite+aiosqlite:///./bot.db` |
| `DEBUG` | Enable SQLAlchemy query echo | `false` |
| `LOG_LEVEL` | Python logging level | `INFO` |

### Production Database (PostgreSQL)

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
```

Install the async driver: `pip install asyncpg`

---

## Running the Service

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your Twilio credentials
```

### 3. Start the server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API documentation is available at `http://localhost:8000/docs`.

### 4. Expose to the internet (Twilio webhook)

Use [ngrok](https://ngrok.com/) or a similar tunnel to expose the local server:

```bash
ngrok http 8000
```

Then set the Twilio WhatsApp sandbox webhook URL to:

```
https://<your-ngrok-id>.ngrok.io/webhook/twilio
```

---

## API Endpoints

### `POST /webhook/twilio`
Receives inbound WhatsApp messages from Twilio. Configured as the webhook URL in the Twilio console.

### `POST /notifications/push`
Send a proactive notification to a specific user. Triggered by external events (e.g., loan approval).

**Request body:**
```json
{
  "recipient": "+18095551234",
  "message": "Your loan LOAN-001 has been approved! 🎉",
  "loan_id": "LOAN-001"
}
```

**Response:**
```json
{
  "success": true,
  "message_sid": "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

### `GET /health`
Service health check. Returns `{"status": "ok"}`.

---

## Conversation Menu

```
👋 Welcome to PayDay Express DR!

1️⃣  FAQ
2️⃣  Check loan status
3️⃣  Contact an advisor
0️⃣  Return to main menu
```

---

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest
```
