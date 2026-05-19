from db.supabase_client import supabase


def create_notification(
    booking_id: str,
    recipient_type: str,
    channel: str,
    title: str,
    message: str,
) -> dict:
    notification_data = {
        "booking_id": booking_id,
        "recipient_type": recipient_type,
        "channel": channel,
        "title": title,
        "message": message,
        "status": "simulated",
    }

    response = (
        supabase
        .table("notifications")
        .insert(notification_data)
        .execute()
    )

    return {
        **notification_data,
        "database_inserted": bool(response.data),
    }


def simulate_notifications(booking: dict) -> dict:
    booking_id = booking.get("booking_id")
    provider_name = booking.get("provider", {}).get("name", "provider")
    assigned_slot = (
        booking.get("scheduling", {}).get("assigned_slot")
    )

    booking_status = booking.get(
    "booking_status",
    "confirmed"
)

    if booking_status == "pending_reschedule":

        user_title = "Alternate slots suggested"

        user_message = (
            f"Selected provider is unavailable for the requested slot. "
            f"Alternate scheduling options were generated for booking "
            f"{booking_id}."
        )

    else:

        user_title = "Booking confirmed"

        user_message = (
            f"Your booking {booking_id} with {provider_name} "
            f"is confirmed for {assigned_slot}."
        )

    user_notification = create_notification(
        booking_id=booking_id,
        recipient_type="user",
        channel="in_app",
        title=user_title,
        message=user_message,
    )

    provider_notification = create_notification(
        booking_id=booking_id,
        recipient_type="provider",
        channel="whatsapp_simulated",
        title="New job assigned",
        message=(
            f"New job assigned for booking {booking_id}. "
            f"Please confirm availability."
        ),
    )

    return {
        "status": "notifications_simulated",
        "booking_id": booking_id,
        "notifications": [
            user_notification,
            provider_notification,
        ],
        "note": (
            "Notifications are persisted as simulated in-app/WhatsApp events. "
            "No real SMS or WhatsApp message is sent."
        ),
    }