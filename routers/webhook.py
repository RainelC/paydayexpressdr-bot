"""Webhook router – handles inbound Twilio WhatsApp messages."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Form, Response
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.orm_models import MessageLog
from models.webhook import InboundMessage, TwilioWebhookPayload
from services.message_parser import process_message
from services.twilio_service import send_whatsapp_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["Webhook"])


@router.post(
    "/twilio",
    summary="Twilio inbound message webhook",
    description=(
        "Receives POST requests from Twilio when a WhatsApp message arrives. "
        "Parses the payload, runs the conversation state machine, "
        "and replies via the Twilio REST API."
    ),
    response_class=Response,
    status_code=200,
)
async def twilio_webhook(
    MessageSid: str = Form(...),
    AccountSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(default=""),
    NumMedia: int = Form(default=0),
    ProfileName: str | None = Form(default=None),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Process an inbound WhatsApp message and send the bot reply."""

    payload = TwilioWebhookPayload(
        MessageSid=MessageSid,
        AccountSid=AccountSid,
        From=From,
        To=To,
        Body=Body,
        NumMedia=NumMedia,
        ProfileName=ProfileName,
    )

    message = InboundMessage(
        message_sid=payload.MessageSid,
        sender=payload.From,
        recipient=payload.To,
        body=payload.Body,
        profile_name=payload.ProfileName,
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

    # Send reply via Twilio REST API
    try:
        out_sid = await send_whatsapp_message(to=message.sender, body=reply_text)
        db.add(
            MessageLog(
                message_sid=out_sid,
                direction="outbound",
                phone_number=message.sender,
                body=reply_text,
            )
        )
        await db.commit()
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to send reply to %s: %s", message.sender, exc)

    # Twilio does not require a TwiML body when we use the REST API to reply
    return Response(status_code=200)
