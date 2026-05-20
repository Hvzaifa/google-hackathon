from datetime import datetime, timedelta, timezone
import random
from db.supabase_client import supabase


def resolve_slot(datetime_preference: str | None) -> str:
    now = datetime.now(timezone.utc)

    if not datetime_preference:
        hours_ahead = random.randint(2, 24)
        return (now + timedelta(hours=hours_ahead)).isoformat()

    text = datetime_preference.lower()

    if "subah" in text or "morning" in text:
        return (now + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0).isoformat()

    if "sham" in text or "evening" in text:
        return (now + timedelta(days=1)).replace(hour=18, minute=0, second=0, microsecond=0).isoformat()

    if "raat" in text or "night" in text:
        return (now + timedelta(days=1)).replace(hour=21, minute=0, second=0, microsecond=0).isoformat()

    if "kal" in text or "tomorrow" in text:
        return (now + timedelta(days=1)).replace(hour=12, minute=0, second=0, microsecond=0).isoformat()

    hours_ahead = random.randint(2, 24)
    return (now + timedelta(hours=hours_ahead)).isoformat()


def calculate_travel_buffer(distance_km: float | None) -> int:
    distance = distance_km or 3.0

    if distance <= 2:
        return 15
    if distance <= 5:
        return 30
    if distance <= 10:
        return 45

    return 60


def check_slot_conflict(provider_name: str, assigned_slot: str) -> dict:
    existing = (
        supabase
        .table("bookings")
        .select("*")
        .eq("provider_name", provider_name)
        .eq("assigned_slot", assigned_slot)
        .execute()
    )

    has_conflict = bool(existing.data)

    return {
        "has_conflict": has_conflict,
        "conflicting_bookings": existing.data or []
    }


def suggest_alternate_slots(assigned_slot: str) -> list[str]:
    base = datetime.fromisoformat(assigned_slot)

    return [
        (base + timedelta(hours=1)).isoformat(),
        (base + timedelta(hours=2)).isoformat(),
        (base + timedelta(days=1)).isoformat(),
    ]


def schedule_booking(intent: dict, selected_provider: dict) -> dict:
    assigned_slot = resolve_slot(
        intent.get("datetime_preference")
    )

    travel_buffer_minutes = calculate_travel_buffer(
        selected_provider.get("distance_km")
    )

    conflict = check_slot_conflict(
        provider_name=selected_provider.get("name"),
        assigned_slot=assigned_slot,
    )

    alternate_slots = []

    scheduling_status = "slot_assigned"

    if conflict["has_conflict"]:
        scheduling_status = "conflict_detected"
        alternate_slots = suggest_alternate_slots(assigned_slot)

    return {
        "assigned_slot": assigned_slot,
        "travel_buffer_minutes": travel_buffer_minutes,
        "slot_conflict_check": conflict,
        "alternate_slots": alternate_slots,
        "scheduling_status": scheduling_status,
    }