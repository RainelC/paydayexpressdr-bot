"""Tests for the push-notification endpoint (/notifications/push)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

PUSH_URL = "/notifications/push"
_MOCK_SID = "SMnotify0000000000000000000000000"


@pytest.mark.asyncio
@patch(
    "routers.notifications.send_whatsapp_message",
    new_callable=AsyncMock,
    return_value=_MOCK_SID,
)
async def test_push_notification_success(mock_send, client: AsyncClient):
    """A valid push request should return success=True and a message_sid."""
    payload = {
        "recipient": "+18095550099",
        "message": "Your loan LOAN-001 has been approved! 🎉",
        "loan_id": "LOAN-001",
    }
    response = await client.post(PUSH_URL, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message_sid"] == _MOCK_SID
    mock_send.assert_awaited_once()


@pytest.mark.asyncio
@patch(
    "routers.notifications.send_whatsapp_message",
    new_callable=AsyncMock,
    side_effect=Exception("Twilio error"),
)
async def test_push_notification_failure(mock_send, client: AsyncClient):
    """When Twilio raises an exception, the endpoint should return success=False."""
    payload = {
        "recipient": "+18095550088",
        "message": "Test failure message",
    }
    response = await client.post(PUSH_URL, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "Twilio error" in data["detail"]


@pytest.mark.asyncio
async def test_push_notification_missing_recipient(client: AsyncClient):
    """A request missing the required 'recipient' field should return 422."""
    payload = {"message": "No recipient provided"}
    response = await client.post(PUSH_URL, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_push_notification_missing_message(client: AsyncClient):
    """A request missing the required 'message' field should return 422."""
    payload = {"recipient": "+18095550077"}
    response = await client.post(PUSH_URL, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
@patch(
    "routers.notifications.send_whatsapp_message",
    new_callable=AsyncMock,
    return_value=_MOCK_SID,
)
async def test_push_notification_without_loan_id(mock_send, client: AsyncClient):
    """loan_id is optional – request should succeed without it."""
    payload = {
        "recipient": "+18095550066",
        "message": "General notification with no loan ID.",
    }
    response = await client.post(PUSH_URL, json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True
