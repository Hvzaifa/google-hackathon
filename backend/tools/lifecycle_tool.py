from datetime import datetime
from db.supabase_client import supabase


def create_booking_event(
    booking_id: str,
    event_type: str,
    status: str,
    message: str,
) -> dict:
    event_data = {
        "booking_id": booking_id,
        "event_type": event_type,
        "status": status,
        "message": message,
    }

    response = (
        supabase
        .table("booking_events")
        .insert(event_data)
        .execute()
    )

    return {
        "event_type": event_type,
        "status": status,
        "message": message,
        "database_inserted": bool(response.data),
        "created_at": datetime.utcnow().isoformat(),
    }


def update_booking_status(
    booking_id: str,
    status: str,
) -> dict:
    response = (
        supabase
        .table("bookings")
        .update({"booking_status": status})
        .eq("booking_id", booking_id)
        .execute()
    )

    return {
        "booking_id": booking_id,
        "new_status": status,
        "database_updated": bool(response.data),
    }


def simulate_booking_lifecycle(booking: dict) -> dict:
    booking_id = booking.get("booking_id")
    provider_name = booking.get("provider", {}).get("name", "provider")

    lifecycle_steps = [
        {
            "event_type": "technician_assigned",
            "status": "technician_assigned",
            "message": f"{provider_name} has accepted the job.",
        },
        {
            "event_type": "on_the_way",
            "status": "on_the_way",
            "message": f"{provider_name} is on the way.",
        },
        {
            "event_type": "service_started",
            "status": "in_progress",
            "message": "Service has started.",
        },
        {
            "event_type": "service_completed",
            "status": "completed",
            "message": "Service completed successfully.",
        },
        {
            "event_type": "feedback_requested",
            "status": "feedback_requested",
            "message": "Please rate your service experience.",
        },
    ]

    events = []

    for step in lifecycle_steps:
        update_booking_status(
            booking_id=booking_id,
            status=step["status"],
        )

        event = create_booking_event(
            booking_id=booking_id,
            event_type=step["event_type"],
            status=step["status"],
            message=step["message"],
        )

        events.append(event)

    return {
        "status": "lifecycle_simulated",
        "booking_id": booking_id,
        "final_status": "feedback_requested",
        "events": events,
        "summary": (
            "Booking lifecycle simulated from technician assignment "
            "to service completion and feedback request."
        ),
    }