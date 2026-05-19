from db.supabase_client import supabase


def analyze_feedback(
    booking: dict,
    rating: int,
    feedback_text: str,
) -> dict:

    feedback_lower = feedback_text.lower()

    complaint_type = None
    sentiment = "positive"

    escalation_required = False

    dispute_severity = "none"

    compensation_amount = 0

    provider_reputation_delta = 0.0

    future_matching_impact = 0.0

    # Complaint detection

    if rating <= 2:
        sentiment = "negative"

    if any(word in feedback_lower for word in [
        "late",
        "delay",
        "waited",
    ]):
        complaint_type = "delay"

    if any(word in feedback_lower for word in [
        "expensive",
        "overcharged",
        "price",
        "zyada paisay",
    ]):
        complaint_type = "price_dispute"

    if any(word in feedback_lower for word in [
        "didn't come",
        "no show",
        "nahi aya",
    ]):
        complaint_type = "provider_no_show"

    if any(word in feedback_lower for word in [
        "bad",
        "poor",
        "issue",
        "problem",
    ]):
        complaint_type = "quality_issue"

    # Severity

    if complaint_type in [
        "provider_no_show",
        "price_dispute",
    ]:
        dispute_severity = "high"
        escalation_required = True
        compensation_amount = 500

    elif complaint_type:
        dispute_severity = "medium"
        compensation_amount = 250

    # Reputation impact

    if rating >= 4:
        provider_reputation_delta = 0.1
        future_matching_impact = 0.05

    elif rating <= 2:
        provider_reputation_delta = -0.3
        future_matching_impact = -0.2

    result = {
        "booking_id": booking.get("booking_id"),

        "provider_name": (
            booking.get("provider_name")
            or booking.get("provider", {}).get("name")
        ),  

        "rating": rating,

        "feedback_text": feedback_text,

        "sentiment": sentiment,

        "complaint_type": complaint_type,

        "dispute_severity": dispute_severity,

        "escalation_required": escalation_required,

        "compensation_amount": compensation_amount,

        "provider_reputation_delta": (
            provider_reputation_delta
        ),

        "future_matching_impact": (
            future_matching_impact
        ),

        "resolution_status": (
            "human_escalation_required"
            if escalation_required
            else "resolved"
        ),
    }

    response = (
        supabase
        .table("service_feedback")
        .insert(result)
        .execute()
    )

    result["database_inserted"] = bool(response.data)

    return result