def calculate_service_price(selected_provider: dict, intent: dict) -> dict:
    base_rate = selected_provider.get("base_rate", 500)
    distance_km = selected_provider.get("distance_km", 3)
    per_km_rate = selected_provider.get("per_km_rate", 30)

    urgency = intent.get("urgency", "scheduled")
    complexity = intent.get("job_complexity", "intermediate")
    budget_sensitivity = intent.get("budget_sensitivity", "unknown")

    urgency_multiplier_map = {
        "urgent": 1.5,
        "same_day": 1.25,
        "scheduled": 1.0,
        "flexible": 0.9,
        "unknown": 1.0,
    }

    complexity_multiplier_map = {
        "basic": 0.85,
        "intermediate": 1.0,
        "complex": 1.4,
        "unknown": 1.0,
    }

    urgency_multiplier = urgency_multiplier_map.get(urgency, 1.0)
    complexity_multiplier = complexity_multiplier_map.get(complexity, 1.0)

    travel_fee = round(distance_km * per_km_rate)

    subtotal_before_multiplier = base_rate + travel_fee

    subtotal_after_multiplier = round(
        subtotal_before_multiplier * urgency_multiplier * complexity_multiplier
    )

    budget_discount = 0

    negotiation_allowed = False

    if budget_sensitivity == "high":
        negotiation_allowed = True
        budget_discount = round(subtotal_after_multiplier * 0.10)

    final_price = subtotal_after_multiplier - budget_discount

    min_estimate = round(final_price * 0.9)
    max_estimate = round(final_price * 1.15)

    breakdown = {
        "base_rate": base_rate,
        "distance_km": distance_km,
        "per_km_rate": per_km_rate,
        "travel_fee": travel_fee,
        "urgency": urgency,
        "urgency_multiplier": urgency_multiplier,
        "job_complexity": complexity,
        "complexity_multiplier": complexity_multiplier,
        "budget_sensitivity": budget_sensitivity,
        "budget_discount": budget_discount,
        "negotiation_allowed": negotiation_allowed,
        "subtotal_before_multiplier": subtotal_before_multiplier,
        "subtotal_after_multiplier": subtotal_after_multiplier,
        "final_price": final_price,
        "min_estimate": min_estimate,
        "max_estimate": max_estimate,
        "currency": "PKR",
    }

    pricing_summary = (
        f"Estimated price is Rs {final_price}. "
        f"This includes Rs {base_rate} base visit fee, "
        f"Rs {travel_fee} travel fee for {distance_km} km, "
        f"{urgency_multiplier}x urgency multiplier, "
        f"{complexity_multiplier}x complexity multiplier"
    )

    if budget_discount > 0:
        pricing_summary += f", and Rs {budget_discount} budget-sensitive discount."

    return {
        "status": "price_calculated",
        "provider_name": selected_provider.get("name"),
        "price": final_price,
        "price_range": {
            "min": min_estimate,
            "max": max_estimate,
            "currency": "PKR",
        },
        "breakdown": breakdown,
        "pricing_summary": pricing_summary,
        "decision_factors": [
            "provider_base_rate",
            "distance",
            "travel_fee",
            "urgency",
            "job_complexity",
            "budget_sensitivity",
            "negotiation_allowed",
        ],
    }