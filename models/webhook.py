"""Pydantic models for inbound Meta WhatsApp Cloud API webhook payloads."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Meta WhatsApp Cloud API nested webhook structure
# ---------------------------------------------------------------------------


class WhatsAppProfile(BaseModel):
    """Sender profile nested inside a contact entry."""

    name: str | None = None


class WhatsAppContact(BaseModel):
    """Contact entry inside the webhook value."""

    profile: WhatsAppProfile = Field(default_factory=WhatsAppProfile)
    wa_id: str = ""


class WhatsAppTextContent(BaseModel):
    """Text content of a message."""

    body: str = ""


class WhatsAppMessage(BaseModel):
    """A single message inside the webhook value."""

    id: str = Field(..., alias="id", description="Unique WhatsApp message ID (wamid.xxx)")
    from_: str = Field(..., alias="from", description="Sender phone number")
    timestamp: str = ""
    type: str = "text"
    text: WhatsAppTextContent = Field(default_factory=WhatsAppTextContent)

    model_config = {"populate_by_name": True}


class WhatsAppMetadata(BaseModel):
    """Metadata about the receiving phone number."""

    display_phone_number: str = ""
    phone_number_id: str = ""


class WhatsAppValue(BaseModel):
    """Value object inside a change entry."""

    messaging_product: str = "whatsapp"
    metadata: WhatsAppMetadata = Field(default_factory=WhatsAppMetadata)
    contacts: list[WhatsAppContact] = Field(default_factory=list)
    messages: list[WhatsAppMessage] = Field(default_factory=list)


class WhatsAppChange(BaseModel):
    """A single change entry."""

    value: WhatsAppValue = Field(default_factory=WhatsAppValue)
    field: str = "messages"


class WhatsAppEntry(BaseModel):
    """A single entry in the webhook payload."""

    id: str = ""
    changes: list[WhatsAppChange] = Field(default_factory=list)


class WhatsAppWebhookPayload(BaseModel):
    """Top-level webhook payload from the Meta WhatsApp Cloud API."""

    object: str = Field("whatsapp_business_account", alias="object")
    entry: list[WhatsAppEntry] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Normalised internal model (unchanged interface)
# ---------------------------------------------------------------------------


class InboundMessage(BaseModel):
    """Normalised inbound message used internally after parsing the webhook."""

    message_sid: str
    sender: str
    recipient: str
    body: str
    profile_name: str | None = None
