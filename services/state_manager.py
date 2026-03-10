"""In-process user-state manager.

Keeps a lightweight dict cache in memory and persists changes to the database
so state survives restarts.  For multi-instance deployments swap the in-memory
dict for Redis using the same interface.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_models import UserState

# In-memory cache: phone_number -> state string
_state_cache: dict[str, str] = {}


async def get_user_state(phone: str, db: AsyncSession) -> str:
    """Return the current conversation state for *phone*, defaulting to MAIN_MENU."""
    if phone in _state_cache:
        return _state_cache[phone]

    result = await db.execute(select(UserState).where(UserState.phone_number == phone))
    row = result.scalar_one_or_none()
    state = row.state if row else "MAIN_MENU"
    _state_cache[phone] = state
    return state


async def set_user_state(phone: str, state: str, db: AsyncSession) -> None:
    """Persist *state* for *phone* in both the cache and the database."""
    _state_cache[phone] = state

    result = await db.execute(select(UserState).where(UserState.phone_number == phone))
    row = result.scalar_one_or_none()
    if row:
        row.state = state
    else:
        db.add(UserState(phone_number=phone, state=state))
    await db.commit()
