from google.cloud.aiplatform import pipeline_job_schedules
import uuid
import random
from datetime import datetime

from db.supabase_client import supabase
from tools.scheduling_tool import schedule_booking
from tools.notification_tool import simulate_notifications
from tools.calendar_tool import simulate_calendar_event
from tools.provider_optimization_tool import generate_provider_optimization_note


def create_booking_record(
    user_id: str,
    intent: dict,
    selected_provider: dict,
    pricing: dict,
) -> dict:

    booking_id = f"SRV-{uuid.uuid4().hex[:8].upper()}"

    eta_minutes = random.randint(20, 90)

    schedule = schedule_booking(
        intent=intent,
        selected_provider=selected_provider,
    )

    provider_optimization = generate_provider_optimization_note(
        selected_provider=selected_provider,
        scheduling=schedule,
    )

    calendar_event = simulate_calendar_event({
        "booking_id": booking_id,
        "scheduling": schedule,
    })

    booking_status = (
        "pending_reschedule"
        if schedule["scheduling_status"] == "conflict_detected"
        else "confirmed"
    )

    notification = simulate_notifications({
        "booking_id": booking_id,
        "booking_status": booking_status,
        "provider": {
            "name": selected_provider.get("name")
        },
        "scheduling": schedule,
        "service_type": intent.get("service_type"),
        "location": intent.get("location"),
        "price": pricing.get("price"),
    })

    booking_data = {
        "booking_id": booking_id,

        "user_id": user_id,

        "provider_name": selected_provider.get("name"),

        "service_type": intent.get("service_type"),

        "issue_description": intent.get("issue_description"),

        "location": intent.get("location"),

        "datetime_preference": intent.get(
            "datetime_preference"
        ),

        "calendar_event_created": True,

        "notification_status": notification["status"],
        
        "payment_status": "confirmed",
        
        "provider_optimization_note": provider_optimization["optimization_note"],

        "booking_status": booking_status,

        "estimated_eta_minutes": eta_minutes,

        "price": pricing.get("price"),

        "currency": pricing.get(
            "price_range",
            {}
        ).get("currency", "PKR"),

        "provider_phone": selected_provider.get(
            "phone",
            "N/A"
        ),

        "provider_rating": selected_provider.get("rating"),

        "provider_distance_km": selected_provider.get(
            "distance_km"
        ),

        "assigned_slot": schedule["assigned_slot"],
        "travel_buffer_minutes": schedule["travel_buffer_minutes"],
        "scheduling_status": schedule["scheduling_status"],
    }

    response = (
        supabase
        .table("bookings")
        .insert(booking_data)
        .execute()
    )

    return {
        "status": booking_status,

        "booking_id": booking_id,

        "booking_status": booking_status,

        "calendar": calendar_event,
        "notifications": notification,
        "provider_optimization": provider_optimization,
        "payment": {
            "status": "confirmed",
            "note": "Payment confirmation simulated."
        },

        "estimated_eta_minutes": eta_minutes,

        "scheduling": schedule,

        "provider": {
            "name": selected_provider.get("name"),
            "rating": selected_provider.get("rating"),
            "distance_km": selected_provider.get(
                "distance_km"
            ),
        },

        "pricing": pricing,

        "database_inserted": bool(response.data),

        "created_at": datetime.utcnow().isoformat(),

        "booking_summary": (
            f"Scheduling conflict detected for {selected_provider.get('name')}. "
            f"Alternate slots were suggested."
            if booking_status == "pending_reschedule"
            else
            f"Booking confirmed with {selected_provider.get('name')}. "
            f"Estimated technician arrival in {eta_minutes} minutes."
        )
    }