from db.supabase_client import supabase


def recover_from_provider_cancellation(
    state: dict
) -> dict:
    booking = state.get("booking", {})
    matching = state.get("matching", {})
    intent = state.get("intent", {})
    user_id = state.get("user_id", "anonymous")

    top_matches = matching.get("top_matches", [])

    cancelled_provider = (
        state.get("selected_provider", {}).get("name")
    )

    replacement = None

    for provider in top_matches:
        if provider.get("name") != cancelled_provider:
            replacement = provider
            break

    recovery_status = (
        "replacement_provider_selected"
        if replacement
        else "waitlisted_no_replacement"
    )

    waitlist_data = {
        "original_booking_id": booking.get("booking_id"),
        "user_id": user_id,
        "cancelled_provider": cancelled_provider,
        "replacement_provider": (
            replacement.get("name") if replacement else None
        ),
        "service_type": intent.get("service_type"),
        "location": intent.get("location"),
        "preferred_time": intent.get("datetime_preference"),
        "status": recovery_status,
        "reason": "Provider cancellation simulation",
    }

    response = (
        supabase
        .table("waitlist_queue")
        .insert(waitlist_data)
        .execute()
    )

    return {
        "status": recovery_status,
        "cancelled_provider": cancelled_provider,
        "replacement_provider": replacement,
        "waitlist_record": waitlist_data,
        "database_inserted": bool(response.data),
        "message": (
            "Replacement provider selected automatically."
            if replacement
            else "No replacement available; request added to waitlist."
        ),
    }