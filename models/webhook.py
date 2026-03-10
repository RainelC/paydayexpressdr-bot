"""Pydantic models for inbound Twilio WhatsApp webhook payloads."""

from pydantic import BaseModel, Field


class TwilioWebhookPayload(BaseModel):
    """Validated model for a Twilio WhatsApp inbound message webhook."""

    MessageSid: str = Field(..., description="Unique Twilio message SID")
    AccountSid: str = Field(..., description="Twilio account SID")
    From: str = Field(..., description="Sender WhatsApp number, e.g. whatsapp:+18095551234")
    To: str = Field(..., description="Receiving WhatsApp number")
    Body: str = Field(default="", description="Text body of the message")
    NumMedia: int = Field(default=0, description="Number of media attachments")
    ProfileName: str | None = Field(None, description="WhatsApp display name of the sender")

    model_config = {"populate_by_name": True}


class InboundMessage(BaseModel):
    """Normalised inbound message used internally after parsing the webhook."""

    message_sid: str
    sender: str
    recipient: str
    body: str
    profile_name: str | None = None
