from db.supabase_client import supabase


def create_completion_evidence_placeholder(booking: dict) -> dict:
    booking_id = booking.get("booking_id")

    evidence = {
        "booking_id": booking_id,
        "completion_checklist": {
            "provider_arrived": False,
            "service_completed": False,
            "customer_confirmed": False,
            "issue_resolved": False,
            "payment_confirmed": False
        },
        "photo_evidence_required": True,
        "photo_evidence_url": None,
        "video_evidence_url": None,
        "evidence_status": "pending_upload"
    }

    response = (
        supabase
        .table("service_completion_evidence")
        .insert(evidence)
        .execute()
    )

    return {
        **evidence,
        "database_inserted": bool(response.data)
    }