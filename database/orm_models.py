"""SQLAlchemy ORM models for user state tracking and message logging."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .connection import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserState(Base):
    """Tracks which menu step a user is currently at in the conversation flow."""

    __tablename__ = "user_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phone_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(50), nullable=False, default="MAIN_MENU")
    context: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


class MessageLog(Base):
    """Audit log of every message sent and received by the bot."""

    __tablename__ = "message_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_sid: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)  # "inbound" | "outbound"
    phone_number: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
