import uuid
import random
from datetime import datetime

from db.supabase_client import supabase


def create_booking_record(
    user_id: str,
    intent: dict,
    selected_provider: dict,
    pricing: dict,
) -> dict:

    booking_id = f"SRV-{uuid.uuid4().hex[:8].upper()}"

    eta_minutes = random.randint(20, 90)

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

        "booking_status": "confirmed",

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
    }

    response = (
        supabase
        .table("bookings")
        .insert(booking_data)
        .execute()
    )

    return {
        "status": "booking_confirmed",

        "booking_id": booking_id,

        "booking_status": "confirmed",

        "estimated_eta_minutes": eta_minutes,

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
            f"Booking confirmed with "
            f"{selected_provider.get('name')}. "
            f"Estimated technician arrival "
            f"in {eta_minutes} minutes."
        )
    }