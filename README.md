# PayDay Express DR – WhatsApp Bot

A professional-grade WhatsApp chatbot built with **FastAPI** and the **Meta WhatsApp Business Cloud API**, designed to handle loan-related customer interactions for PayDay Express DR.

## Features

- **Inbound message handling** via a Meta WhatsApp Cloud API webhook with a guided menu (FAQ, loan status, contact)
- **Webhook verification** endpoint for the Meta App Dashboard registration flow
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
│   ├── webhook.py           # GET /webhook/whatsapp (verification) & POST /webhook/whatsapp (inbound)
│   └── notifications.py     # POST /notifications/push – outbound push endpoint
├── services/
│   ├── message_parser.py    # Conversation state machine & FAQ logic
│   ├── state_manager.py     # In-memory + DB state cache
│   └── whatsapp_service.py  # Async Meta WhatsApp Cloud API client
├── models/
│   ├── webhook.py           # Pydantic schemas for Meta WhatsApp webhook payload
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
| `WHATSAPP_API_TOKEN` | Permanent access token from the Meta App Dashboard | *(required)* |
| `WHATSAPP_PHONE_NUMBER_ID` | Phone Number ID from the Meta WhatsApp Business settings | *(required)* |
| `WHATSAPP_VERIFY_TOKEN` | A secret string you choose for webhook verification | *(required)* |
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
# Edit .env with your Meta WhatsApp Business API credentials
```

### 3. Start the server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API documentation is available at `http://localhost:8000/docs`.

### 4. Expose to the internet (Meta webhook)

Use [ngrok](https://ngrok.com/) or a similar tunnel to expose the local server:

```bash
ngrok http 8000
```

Then set the Meta WhatsApp webhook URL in the App Dashboard to:

```
https://<your-ngrok-id>.ngrok.io/webhook/whatsapp
```

---

## API Endpoints

### `GET /webhook/whatsapp`
Handles the one-time verification challenge sent by Meta when registering the webhook URL. Returns the `hub.challenge` value when the `hub.verify_token` matches.

### `POST /webhook/whatsapp`
Receives inbound WhatsApp messages from the Meta Cloud API. Configured as the webhook URL in the Meta App Dashboard.

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
  "message_sid": "wamid.xxxxxxxxxxxxxxxx"
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
