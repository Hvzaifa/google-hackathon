from fastapi import APIRouter

from db.supabase_client import supabase
from schemas.request_schemas import SelectSlotRequest

router = APIRouter(prefix="/api", tags=["booking"])



@router.get("/booking-status/{booking_id}")
def booking_status(booking_id: str):
    booking = (
        supabase
        .table("bookings")
        .select("*")
        .eq("booking_id", booking_id)
        .execute()
    )

    events = (
        supabase
        .table("booking_events")
        .select("*")
        .eq("booking_id", booking_id)
        .order("created_at")
        .execute()
    )

    return {
        "booking": booking.data[0] if booking.data else None,
        "events": events.data,
    }


@router.get("/booking-events/{booking_id}")
def get_booking_events(booking_id: str):
    result = (
        supabase
        .table("booking_events")
        .select("*")
        .eq("booking_id", booking_id)
        .order("created_at")
        .execute()
    )

    return {
        "booking_id": booking_id,
        "events": result.data,
    }

@router.get("/notifications/{booking_id}")
def get_notifications(booking_id: str):
    result = (
        supabase
        .table("notifications")
        .select("*")
        .eq("booking_id", booking_id)
        .order("created_at")
        .execute()
    )

    return {
        "booking_id": booking_id,
        "notifications": result.data,
    }


@router.post("/booking/{booking_id}/select-slot")
def select_alternate_slot(booking_id: str, body: SelectSlotRequest):
    response = (
        supabase
        .table("bookings")
        .update({
            "assigned_slot": body.selected_slot,
            "booking_status": "confirmed",
            "scheduling_status": "slot_assigned"
        })
        .eq("booking_id", booking_id)
        .execute()
    )

    return {
        "status": "slot_confirmed",
        "booking_id": booking_id,
        "selected_slot": body.selected_slot,
        "database_updated": bool(response.data),
        "message": "Alternate slot selected and booking confirmed."
    }