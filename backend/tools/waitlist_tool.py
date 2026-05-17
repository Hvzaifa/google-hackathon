"""
In-memory waitlist store for ServisAI.
When all providers at a requested slot are booked, the user is queued.
When a slot opens (simulated), the next user in queue is auto-rescheduled.
"""
from __future__ import annotations
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

# Structure: { "provider_name::YYYY-MM-DD HH:MM": [{"user_id", "booking_ref", "queued_at"}, ...] }
_waitlist: Dict[str, List[dict]] = {}

def add_to_waitlist(provider_name: str, appointment_time: str, user_id: str, booking_ref: str) -> str:
    """Add a user to the waitlist for a provider+slot. Returns a waitlist_id."""
    key = f"{provider_name}::{appointment_time}"
    entry = {
        "user_id": user_id,
        "booking_ref": booking_ref,
        "queued_at": time.time(),
        "waitlist_id": f"WL-{int(time.time())}-{len(_waitlist.get(key, []))}"
    }
    _waitlist.setdefault(key, []).append(entry)
    return entry["waitlist_id"]

def get_waitlist_position(provider_name: str, appointment_time: str, user_id: str) -> int:
    """Returns 1-based queue position, or -1 if not in queue."""
    key = f"{provider_name}::{appointment_time}"
    for i, entry in enumerate(_waitlist.get(key, [])):
        if entry["user_id"] == user_id:
            return i + 1
    return -1

def auto_reschedule_next(provider_name: str, appointment_time: str) -> Optional[dict]:
    """
    Simulates a slot opening. Pops the first user from the waitlist for this slot,
    assigns them the slot, and returns their entry with an auto_rescheduled_to field.
    Returns None if the waitlist is empty.
    """
    key = f"{provider_name}::{appointment_time}"
    queue = _waitlist.get(key, [])
    if not queue:
        return None
    next_user = queue.pop(0)
    next_user["auto_rescheduled_to"] = appointment_time
    next_user["confirmed_at"] = time.time()
    return next_user

def get_next_available_slot(appointment_time: str, hours_ahead: int = 2) -> str:
    """Returns a slot string shifted forward by hours_ahead hours."""
    try:
        dt = datetime.strptime(appointment_time, "%Y-%m-%d %H:%M")
    except ValueError:
        dt = datetime.now()
    new_dt = dt + timedelta(hours=hours_ahead)
    return new_dt.strftime("%Y-%m-%d %H:%M")
