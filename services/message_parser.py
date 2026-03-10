"""Core conversation logic: state machine, menu rendering, and FAQ answers."""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from models.webhook import InboundMessage
from services.state_manager import get_user_state, set_user_state

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Static content
# ---------------------------------------------------------------------------

MAIN_MENU = (
    "👋 Welcome to *PayDay Express DR*!\n\n"
    "Please choose an option:\n"
    "1️⃣  Frequently Asked Questions (FAQ)\n"
    "2️⃣  Check loan status\n"
    "3️⃣  Contact an advisor\n"
    "0️⃣  Return to main menu\n\n"
    "_Reply with the number of your choice._"
)

FAQ_MENU = (
    "📖 *Frequently Asked Questions*\n\n"
    "1️⃣  What are the loan requirements?\n"
    "2️⃣  How long does approval take?\n"
    "3️⃣  What interest rates apply?\n"
    "4️⃣  How do I repay?\n"
    "5️⃣  Is my data safe?\n"
    "0️⃣  Return to main menu\n\n"
    "_Reply with the number of your choice._"
)

FAQ_ANSWERS: dict[str, str] = {
    "1": (
        "📋 *Loan Requirements*\n\n"
        "• Valid national ID (Cédula)\n"
        "• Proof of income (pay stub or bank statement)\n"
        "• Active bank account\n"
        "• Age 18–65\n\n"
        "Reply *0* to return to the main menu."
    ),
    "2": (
        "⏱ *Approval Time*\n\n"
        "Applications are reviewed within *24–48 business hours*. "
        "You will receive an SMS/WhatsApp notification once a decision has been made.\n\n"
        "Reply *0* to return to the main menu."
    ),
    "3": (
        "💰 *Interest Rates*\n\n"
        "Our rates range from *3% to 8% monthly* depending on the loan amount "
        "and repayment term. A full breakdown is provided before you sign.\n\n"
        "Reply *0* to return to the main menu."
    ),
    "4": (
        "🔄 *Repayment Options*\n\n"
        "• Automatic bank debit on payday\n"
        "• Online transfer to our account\n"
        "• In-person payment at any branch\n\n"
        "Reply *0* to return to the main menu."
    ),
    "5": (
        "🔒 *Data Privacy*\n\n"
        "Your data is protected under Dominican Republic Law 172-13 on Personal Data "
        "and is never shared with third parties without your explicit consent.\n\n"
        "Reply *0* to return to the main menu."
    ),
}

STATUS_PROMPT = (
    "🔍 *Loan Status Lookup*\n\n"
    "Please reply with your *Loan ID* (e.g. LOAN-12345) to retrieve your current status.\n\n"
    "Reply *0* to return to the main menu."
)

CONTACT_MESSAGE = (
    "📞 *Contact an Advisor*\n\n"
    "Our advisors are available Monday–Friday, 8 am – 6 pm (AST).\n\n"
    "• Phone: +1 (809) 555-0100\n"
    "• Email: support@paydayexpressdr.com\n"
    "• WhatsApp: this number\n\n"
    "Reply *0* to return to the main menu."
)

UNKNOWN_OPTION = (
    "❓ I didn't understand that option. Please reply with a number from the menu.\n\n"
    + MAIN_MENU
)


# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------


async def process_message(message: InboundMessage, db: AsyncSession) -> str:
    """Process an inbound message and return the bot reply text.

    Implements a simple two-level state machine:

    * MAIN_MENU  – top-level option selection
    * FAQ_MENU   – sub-menu option selection
    * LOAN_STATUS – awaiting user's loan ID input
    """
    phone = message.sender
    user_input = message.body.strip()
    current_state = await get_user_state(phone, db)

    logger.debug("process_message phone=%s state=%s input=%r", phone, current_state, user_input)

    # ── MAIN MENU ──────────────────────────────────────────────────────────
    if current_state == "MAIN_MENU":
        if user_input == "1":
            await set_user_state(phone, "FAQ_MENU", db)
            return FAQ_MENU
        if user_input == "2":
            await set_user_state(phone, "LOAN_STATUS", db)
            return STATUS_PROMPT
        if user_input == "3":
            return CONTACT_MESSAGE
        if user_input == "0":
            return MAIN_MENU
        # First contact or unrecognised – show main menu
        return MAIN_MENU

    # ── FAQ MENU ───────────────────────────────────────────────────────────
    if current_state == "FAQ_MENU":
        if user_input == "0":
            await set_user_state(phone, "MAIN_MENU", db)
            return MAIN_MENU
        if user_input in FAQ_ANSWERS:
            return FAQ_ANSWERS[user_input]
        return FAQ_MENU

    # ── LOAN STATUS ────────────────────────────────────────────────────────
    if current_state == "LOAN_STATUS":
        if user_input == "0":
            await set_user_state(phone, "MAIN_MENU", db)
            return MAIN_MENU
        # In a real system this would query a loans DB; we return a stub.
        reply = _mock_loan_status(user_input)
        await set_user_state(phone, "MAIN_MENU", db)
        return reply

    # Fallback – reset to main menu
    await set_user_state(phone, "MAIN_MENU", db)
    return MAIN_MENU


def _mock_loan_status(loan_id: str) -> str:
    """Return a stub loan-status response (replace with real DB query)."""
    loan_id_upper = loan_id.upper()
    return (
        f"📊 *Status for {loan_id_upper}*\n\n"
        "• Status: *Under Review* ✅\n"
        "• Submitted: 2026-03-08\n"
        "• Expected decision: within 48 h\n\n"
        "You will be notified automatically when the status changes.\n\n"
        "Reply *0* to return to the main menu."
    )
