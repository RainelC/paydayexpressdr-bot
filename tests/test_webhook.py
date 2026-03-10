"""Tests for the Twilio inbound webhook endpoint (/webhook/twilio)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

WEBHOOK_URL = "/webhook/twilio"

_MOCK_SID = "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def _webhook_form(body: str, from_: str = "whatsapp:+18095550001") -> dict:
    return {
        "MessageSid": "SMtest123",
        "AccountSid": "ACtest",
        "From": from_,
        "To": "whatsapp:+14155238886",
        "Body": body,
        "NumMedia": "0",
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """The /health endpoint should return 200 with status ok."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
@patch("routers.webhook.send_whatsapp_message", new_callable=AsyncMock, return_value=_MOCK_SID)
async def test_webhook_returns_200(mock_send, client: AsyncClient):
    """Webhook should return HTTP 200 for any valid payload."""
    response = await client.post(WEBHOOK_URL, data=_webhook_form("hello"))
    assert response.status_code == 200


@pytest.mark.asyncio
@patch("routers.webhook.send_whatsapp_message", new_callable=AsyncMock, return_value=_MOCK_SID)
async def test_first_contact_shows_main_menu(mock_send, client: AsyncClient):
    """An unrecognised first message should trigger the main menu reply."""
    await client.post(WEBHOOK_URL, data=_webhook_form("hi there"))
    call_args = mock_send.call_args
    reply_body: str = call_args.kwargs.get("body") or call_args.args[1]
    assert "FAQ" in reply_body or "Welcome" in reply_body


@pytest.mark.asyncio
@patch("routers.webhook.send_whatsapp_message", new_callable=AsyncMock, return_value=_MOCK_SID)
async def test_option_1_shows_faq_menu(mock_send, client: AsyncClient):
    """Sending '1' from the main menu should return the FAQ sub-menu."""
    await client.post(WEBHOOK_URL, data=_webhook_form("1"))
    call_args = mock_send.call_args
    reply_body: str = call_args.kwargs.get("body") or call_args.args[1]
    assert "FAQ" in reply_body or "Frequently" in reply_body


@pytest.mark.asyncio
@patch("routers.webhook.send_whatsapp_message", new_callable=AsyncMock, return_value=_MOCK_SID)
async def test_faq_answer_returned(mock_send, client: AsyncClient):
    """After entering the FAQ sub-menu, selecting '1' should return the requirements answer."""
    phone = "whatsapp:+18095550010"

    # Enter FAQ menu
    await client.post(WEBHOOK_URL, data=_webhook_form("1", from_=phone))

    # Select FAQ item 1
    mock_send.reset_mock()
    await client.post(WEBHOOK_URL, data=_webhook_form("1", from_=phone))
    call_args = mock_send.call_args
    reply_body: str = call_args.kwargs.get("body") or call_args.args[1]
    assert "Requirement" in reply_body or "Cédula" in reply_body


@pytest.mark.asyncio
@patch("routers.webhook.send_whatsapp_message", new_callable=AsyncMock, return_value=_MOCK_SID)
async def test_option_2_shows_status_prompt(mock_send, client: AsyncClient):
    """Sending '2' from the main menu should trigger the loan-status prompt."""
    phone = "whatsapp:+18095550020"
    await client.post(WEBHOOK_URL, data=_webhook_form("2", from_=phone))
    call_args = mock_send.call_args
    reply_body: str = call_args.kwargs.get("body") or call_args.args[1]
    assert "Loan" in reply_body or "status" in reply_body.lower()


@pytest.mark.asyncio
@patch("routers.webhook.send_whatsapp_message", new_callable=AsyncMock, return_value=_MOCK_SID)
async def test_loan_id_lookup(mock_send, client: AsyncClient):
    """After the status prompt, sending a loan ID should return a status response."""
    phone = "whatsapp:+18095550030"

    # Trigger status prompt
    await client.post(WEBHOOK_URL, data=_webhook_form("2", from_=phone))

    # Submit loan ID
    mock_send.reset_mock()
    await client.post(WEBHOOK_URL, data=_webhook_form("LOAN-99999", from_=phone))
    call_args = mock_send.call_args
    reply_body: str = call_args.kwargs.get("body") or call_args.args[1]
    assert "LOAN-99999" in reply_body.upper()


@pytest.mark.asyncio
@patch("routers.webhook.send_whatsapp_message", new_callable=AsyncMock, return_value=_MOCK_SID)
async def test_return_to_main_menu(mock_send, client: AsyncClient):
    """Sending '0' from a sub-menu should return the main menu."""
    phone = "whatsapp:+18095550040"

    # Enter FAQ menu
    await client.post(WEBHOOK_URL, data=_webhook_form("1", from_=phone))

    # Send '0' to go back
    mock_send.reset_mock()
    await client.post(WEBHOOK_URL, data=_webhook_form("0", from_=phone))
    call_args = mock_send.call_args
    reply_body: str = call_args.kwargs.get("body") or call_args.args[1]
    assert "Welcome" in reply_body or "main menu" in reply_body.lower()
