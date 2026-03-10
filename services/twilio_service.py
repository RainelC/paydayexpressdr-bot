"""Async Twilio WhatsApp client wrapper."""

from __future__ import annotations

import logging

import httpx

from database.config import settings

logger = logging.getLogger(__name__)

_TWILIO_MESSAGES_URL = (
    f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Messages.json"
)


async def send_whatsapp_message(to: str, body: str) -> str:
    """Send a WhatsApp message via Twilio and return the resulting MessageSid.

    *to* must already include the ``whatsapp:`` prefix (e.g. ``whatsapp:+18095551234``).
    If it does not, the prefix is added automatically.
    """
    if not to.startswith("whatsapp:"):
        to = f"whatsapp:{to}"

    payload = {
        "From": settings.twilio_whatsapp_from,
        "To": to,
        "Body": body,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            _TWILIO_MESSAGES_URL,
            data=payload,
            auth=(settings.twilio_account_sid, settings.twilio_auth_token),
            timeout=10.0,
        )

    response.raise_for_status()
    data = response.json()
    message_sid: str = data["sid"]
    logger.info("Sent WhatsApp message sid=%s to=%s", message_sid, to)
    return message_sid
