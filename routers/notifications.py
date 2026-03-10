"""Notifications router – push outbound status-change messages to users."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.orm_models import MessageLog
from models.notification import PushNotificationRequest, PushNotificationResponse
from services.whatsapp_service import send_whatsapp_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post(
    "/push",
    summary="Send a proactive push notification",
    description=(
        "Triggered by external systems (e.g. a loan-management platform) to send "
        "a proactive WhatsApp message to a specific user when their loan status changes."
    ),
    response_model=PushNotificationResponse,
    status_code=200,
)
async def push_notification(
    request: PushNotificationRequest,
    db: AsyncSession = Depends(get_db),
) -> PushNotificationResponse:
    """Dispatch a push notification to the specified WhatsApp number."""

    try:
        message_sid = await send_whatsapp_message(to=request.recipient, body=request.message)
        db.add(
            MessageLog(
                message_sid=message_sid,
                direction="outbound",
                phone_number=request.recipient,
                body=request.message,
            )
        )
        await db.commit()
        return PushNotificationResponse(success=True, message_sid=message_sid)
    except Exception as exc:  # noqa: BLE001
        logger.error("push_notification failed for %s: %s", request.recipient, exc)
        return PushNotificationResponse(success=False, detail=str(exc))
