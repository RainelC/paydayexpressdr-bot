"""Webhook router – handles inbound Meta WhatsApp Cloud API messages."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from database.config import settings
from database.connection import get_db
from database.orm_models import MessageLog
from models.webhook import InboundMessage, WhatsAppWebhookPayload
from services.message_parser import process_message
from services.whatsapp_service import send_whatsapp_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["Webhook"])


@router.get(
    "/whatsapp",
    summary="Meta WhatsApp webhook verification",
    description=(
        "Handles the one-time verification challenge sent by Meta "
        "when you register the webhook URL in the App Dashboard."
    ),
    status_code=200,
)
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
) -> Response:
    """Return the challenge token when the verify token matches."""
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        logger.info("Webhook verified successfully")
        return Response(content=hub_challenge, media_type="text/plain")
    logger.warning("Webhook verification failed – token mismatch")
    return Response(status_code=403)


@router.post(
    "/whatsapp",
    summary="Meta WhatsApp inbound message webhook",
    description=(
        "Receives POST requests from the Meta WhatsApp Cloud API when a "
        "WhatsApp message arrives. Parses the payload, runs the conversation "
        "state machine, and replies via the WhatsApp Cloud API."
    ),
    response_class=Response,
    status_code=200,
)
async def whatsapp_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Process an inbound WhatsApp message and send the bot reply."""

    body = await request.json()
    payload = WhatsAppWebhookPayload.model_validate(body)

    # Iterate over all entries and changes to find text messages
    for entry in payload.entry:
        for change in entry.changes:
            value = change.value
            for msg in value.messages:
                if msg.type != "text":
                    continue

                # Resolve profile name from contacts if available
                profile_name: str | None = None
                if value.contacts:
                    profile_name = value.contacts[0].profile.name

                phone_number_id = value.metadata.phone_number_id

                message = InboundMessage(
                    message_sid=msg.id,
                    sender=msg.from_,
                    recipient=phone_number_id,
                    body=msg.text.body,
                    profile_name=profile_name,
                )

                # Persist inbound log
                db.add(
                    MessageLog(
                        message_sid=message.message_sid,
                        direction="inbound",
                        phone_number=message.sender,
                        body=message.body,
                    )
                )
                await db.commit()

                reply_text = await process_message(message, db)

                # Send reply via Meta WhatsApp Cloud API
                try:
                    out_id = await send_whatsapp_message(to=message.sender, body=reply_text)
                    db.add(
                        MessageLog(
                            message_sid=out_id,
                            direction="outbound",
                            phone_number=message.sender,
                            body=reply_text,
                        )
                    )
                    await db.commit()
                except Exception as exc:  # noqa: BLE001
                    logger.error("Failed to send reply to %s: %s", message.sender, exc)

    return Response(status_code=200)
