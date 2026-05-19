def format_trace_timeline(agent_trace: list) -> list:
    timeline = []

    for step in agent_trace or []:
        timeline.append({
            "step": step.get("step"),
            "tool_called": step.get("tool_called"),
            "duration_ms": step.get("duration_ms"),
            "summary": (
                step.get("output", {}).get("summary")
                or step.get("output", {}).get("status")
            ),
            "input": step.get("input"),
            "output": step.get("output"),
        })

    return timeline


def format_orchestration_response(final_state: dict) -> dict:
    selected_provider = None

    if final_state.get("matching"):
        selected_provider = (
            final_state.get("selected_provider")
            or final_state
                .get("matching", {})
                .get("selected_provider")
        )

    pricing = final_state.get("pricing")
    booking = final_state.get("booking")
    lifecycle = final_state.get("lifecycle")

    return {
        "status": final_state.get("pipeline_status"),
        "fallback_response": final_state.get("fallback_response"),

        "completion_evidence": final_state.get("completion_evidence"),
        "cancellation_fallback": final_state.get("cancellation_fallback"),
        "payment_fallback": final_state.get("payment_fallback"),

        "request_understanding": {
            "service_type": final_state.get("intent", {}).get("service_type"),
            "issue_description": final_state.get("intent", {}).get("issue_description"),
            "location": final_state.get("intent", {}).get("location"),
            "datetime_preference": final_state.get("intent", {}).get("datetime_preference"),
            "urgency": final_state.get("intent", {}).get("urgency"),
            "language_detected": final_state.get("intent", {}).get("language_detected"),
            "confidence": final_state.get("intent", {}).get("confidence"),
            "missing_fields": final_state.get("intent", {}).get("missing_fields"),
            "clarification_question": final_state.get("intent", {}).get("clarification_question"),
        },

        "selected_provider": {
            "name": selected_provider.get("name") if selected_provider else None,
            "address": selected_provider.get("address") if selected_provider else None,
            "rating": selected_provider.get("rating") if selected_provider else None,
            "distance_km": selected_provider.get("distance_km") if selected_provider else None,
            "matching_score": selected_provider.get("final_matching_score") if selected_provider else None,
            "source": selected_provider.get("source") if selected_provider else None,
        } if selected_provider else None,

        "top_matches": [
            {
                "name": p.get("name"),
                "rating": p.get("rating"),
                "distance_km": p.get("distance_km"),
                "matching_score": p.get("final_matching_score"),
                "address": p.get("address"),
                "matching_scores": p.get("matching_scores"),
            }
            for p in final_state.get("matching", {}).get("top_matches", [])
        ],

        "matching_reason": final_state.get("matching", {}).get("ranking_summary"),

        "pricing": {
            "price": pricing.get("price") if pricing else None,
            "currency": pricing.get("price_range", {}).get("currency") if pricing else "PKR",
            "range": pricing.get("price_range") if pricing else None,
            "summary": pricing.get("pricing_summary") if pricing else None,
            "breakdown": pricing.get("breakdown") if pricing else None,
        } if pricing else None,

        "booking": {
            "booking_id": booking.get("booking_id") if booking else None,
            "status": booking.get("booking_status") if booking else None,
            "eta_minutes": booking.get("estimated_eta_minutes") if booking else None,
            "scheduling": booking.get("scheduling") if booking else None,

            "calendar": booking.get("calendar") if booking else None,
            "notifications": booking.get("notifications") if booking else None,
            "provider_optimization": booking.get("provider_optimization") if booking else None,
            "payment": booking.get("payment") if booking else None,
            "summary": booking.get("booking_summary") if booking else None,
            "database_inserted": booking.get("database_inserted") if booking else None,
        } if booking else None,

        "lifecycle": {
            "status": lifecycle.get("status") if lifecycle else None,
            "final_status": lifecycle.get("final_status") if lifecycle else None,
            "events": lifecycle.get("events") if lifecycle else [],
            "summary": lifecycle.get("summary") if lifecycle else None,
        } if lifecycle else None,

        "agent_trace": format_trace_timeline(
            final_state.get("agent_trace", [])
        ),
    }