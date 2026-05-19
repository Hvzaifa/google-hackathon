def simulate_calendar_event(booking: dict) -> dict:
    scheduling = booking.get("scheduling", {})

    return {
        "status": "calendar_event_simulated",
        "booking_id": booking.get("booking_id"),
        "assigned_slot": scheduling.get("assigned_slot"),
        "travel_buffer_minutes": scheduling.get("travel_buffer_minutes"),
        "calendar_provider": "simulated_calendar",
        "note": "Calendar update simulated for hackathon prototype."
    }