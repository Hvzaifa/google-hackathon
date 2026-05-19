from db.supabase_client import supabase


def update_provider_reputation(feedback: dict) -> dict:
    provider_name = feedback.get("provider_name")

    if not provider_name:
        return {
            "status": "skipped",
            "reason": "provider_name missing"
        }

    existing = (
        supabase
        .table("provider_reputation")
        .select("*")
        .eq("provider_name", provider_name)
        .execute()
    )

    rating = feedback.get("rating", 3)
    reputation_delta = feedback.get("provider_reputation_delta", 0)
    future_impact = feedback.get("future_matching_impact", 0)

    if existing.data:
        current = existing.data[0]

        old_count = current.get("total_feedback_count", 0)
        old_avg = current.get("average_rating", 0)
        old_score = current.get("reputation_score", 0.75)

        new_count = old_count + 1
        new_avg = ((old_avg * old_count) + rating) / new_count
        new_score = max(0, min(1, old_score + reputation_delta))

        response = (
            supabase
            .table("provider_reputation")
            .update({
                "total_feedback_count": new_count,
                "average_rating": round(new_avg, 2),
                "reputation_score": round(new_score, 2),
                "future_matching_impact": future_impact,
                "last_feedback_summary": feedback.get("feedback_text"),
            })
            .eq("provider_name", provider_name)
            .execute()
        )

        return {
            "status": "updated",
            "provider_name": provider_name,
            "new_average_rating": round(new_avg, 2),
            "new_reputation_score": round(new_score, 2),
            "future_matching_impact": future_impact,
            "database_updated": bool(response.data),
        }

    response = (
        supabase
        .table("provider_reputation")
        .insert({
            "provider_name": provider_name,
            "total_feedback_count": 1,
            "average_rating": rating,
            "reputation_score": max(0, min(1, 0.75 + reputation_delta)),
            "future_matching_impact": future_impact,
            "last_feedback_summary": feedback.get("feedback_text"),
        })
        .execute()
    )

    return {
        "status": "created",
        "provider_name": provider_name,
        "new_average_rating": rating,
        "new_reputation_score": max(0, min(1, 0.75 + reputation_delta)),
        "future_matching_impact": future_impact,
        "database_inserted": bool(response.data),
    }