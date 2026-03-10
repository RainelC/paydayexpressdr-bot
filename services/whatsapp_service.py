"""Async Meta WhatsApp Business API client wrapper."""

from __future__ import annotations

import logging

import httpx

from database.config import settings

logger = logging.getLogger(__name__)

_WHATSAPP_API_URL = (
    f"https://graph.facebook.com/v21.0/{settings.whatsapp_phone_number_id}/messages"
)


async def send_whatsapp_message(to: str, body: str) -> str:
    """Send a WhatsApp message via the Meta Cloud API and return the message ID.

    *to* should be in E.164 format (e.g. ``+18095551234``).
    Any ``whatsapp:`` prefix is stripped automatically for backwards compatibility.
    """
    if to.startswith("whatsapp:"):
        to = to[len("whatsapp:"):]

    # Meta API expects digits only (no leading '+')
    to = to.lstrip("+")

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }

    headers = {
        "Authorization": f"Bearer {settings.whatsapp_api_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            _WHATSAPP_API_URL,
            json=payload,
            headers=headers,
            timeout=10.0,
        )

    response.raise_for_status()
    data = response.json()
    message_id: str = data["messages"][0]["id"]
    logger.info("Sent WhatsApp message id=%s to=%s", message_id, to)
    return message_id
