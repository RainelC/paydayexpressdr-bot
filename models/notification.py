"""Pydantic models for outbound push-notification requests."""

from pydantic import BaseModel, Field


class PushNotificationRequest(BaseModel):
    """Payload accepted by the /notifications/push endpoint."""

    recipient: str = Field(
        ...,
        description="Destination WhatsApp number in E.164 format, e.g. +18095551234",
        examples=["+18095551234"],
    )
    message: str = Field(..., description="Text message to deliver to the user")
    loan_id: str | None = Field(None, description="Optional loan / case reference ID")


class PushNotificationResponse(BaseModel):
    """Response returned after dispatching a push notification."""

    success: bool
    message_sid: str | None = None
    detail: str | None = None
