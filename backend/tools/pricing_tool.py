"""
Deterministic pricing math engine for ServisAI.
Computes price breakdowns, surcharges, and materials cost estimates in Python.
"""

from typing import Dict, Any
from schemas.matching_schema import ProviderCandidate, IntentData
from schemas.pricing_schema import PriceBreakdown, PricingOutput


def estimate_materials_cost(service_type: str, job_complexity: str) -> float:
    """
    Estimate typical materials cost based on service type and job complexity.
    Values are in PKR (Pakistani Rupees).
    """
    service = (service_type or "other").lower()
    complexity = (job_complexity or "unknown").lower()

    # Materials cost lookup
    # key: (service_type_substring, complexity)
    materials_matrix = {
        # AC repair materials
        ("ac", "basic"): 0.0,
        ("ac", "intermediate"): 1200.0,  # e.g., Capacitor, sensor, cleaning solution
        ("ac", "complex"): 4500.0,       # e.g., Gas refill, valve replacement, circuit board
        # Electrician materials
        ("elect", "basic"): 150.0,       # Tape, simple fuse
        ("elect", "intermediate"): 800.0, # Switch, sockets, wiring length
        ("elect", "complex"): 3000.0,     # Distribution board, circuit breaker, main wire
        # Plumber materials
        ("plumb", "basic"): 200.0,       # Teflon tape, washers
        ("plumb", "intermediate"): 1000.0, # Pipe connectors, valves, taps
        ("plumb", "complex"): 3500.0,     # Water pump motor winding, main line, heavy valves
    }

    # Match by substring
    for (s_key, c_key), cost in materials_matrix.items():
        if s_key in service and c_key == complexity:
            return cost

    # Default fallback matrix
    default_matrix = {
        "basic": 0.0,
        "intermediate": 500.0,
        "complex": 2000.0,
        "unknown": 250.0
    }
    return default_matrix.get(complexity, 250.0)


def calculate_service_price(provider: ProviderCandidate, intent: IntentData) -> PriceBreakdown:
    """
    Deterministically calculate detailed service price.
    
    Formula:
      Subtotal = (Base Rate + Distance Fare) * Urgency Multiplier * Complexity Multiplier * Surge Multiplier - Loyalty Discount
      Total Price = Subtotal + Materials Cost
    """
    base_fare = float(provider.base_rate)
    distance_fare = float(provider.per_km_rate * provider.distance_km)
    base_plus_dist = base_fare + distance_fare

    # 1. Urgency multiplier
    urgency = (intent.urgency or "unknown").lower()
    if urgency == "urgent":
        urgency_multiplier = 1.30
    elif urgency == "same_day":
        urgency_multiplier = 1.15
    else:
        urgency_multiplier = 1.0

    # 2. Complexity multiplier
    complexity = (intent.job_complexity or "unknown").lower()
    if complexity == "basic":
        complexity_multiplier = 1.0
    elif complexity == "intermediate":
        complexity_multiplier = 1.30
    elif complexity == "complex":
        complexity_multiplier = 1.80
    else:
        complexity_multiplier = 1.10

    # 3. Surge & Loyalty
    # Surge based on high urgency or complex same day jobs
    surge_multiplier = 1.10 if (urgency == "urgent" and complexity == "complex") else 1.0
    # Loyalty discount of PKR 50 if user has preferences/loyalty
    loyalty_discount = 50.0 if len(intent.user_preferences) > 0 else 0.0

    # Calculate subtotal using precise requirements formula
    subtotal = (base_plus_dist * urgency_multiplier * complexity_multiplier * surge_multiplier) - loyalty_discount

    # Derive surcharges for transparent breakdown
    urgency_surcharge = round(base_plus_dist * (urgency_multiplier - 1.0), 2)
    complexity_surcharge = round((base_plus_dist * urgency_multiplier) * (complexity_multiplier - 1.0), 2)

    # 4. Materials cost
    materials_cost = estimate_materials_cost(intent.service_type or "other", complexity)

    # 5. Total Price
    total_price = round(max(subtotal + materials_cost, 0.0), 2)

    return PriceBreakdown(
        base_fare=base_fare,
        distance_fare=distance_fare,
        urgency_surcharge=urgency_surcharge,
        complexity_surcharge=complexity_surcharge,
        materials_cost=materials_cost,
        surge_multiplier=surge_multiplier,
        loyalty_discount=loyalty_discount,
        total_price=total_price,
        currency="PKR"
    )
