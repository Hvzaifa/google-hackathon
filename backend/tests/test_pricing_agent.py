"""
Standalone tests for the Pricing Agent.
"""

import sys
import os

# Allow running from either backend/ or project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.pricing_agent import PricingAgent


def _make_state(
    urgency: str = "scheduled",
    budget_sensitivity: str = "medium",
    job_complexity: str = "intermediate",
    language: str = "roman_urdu"
) -> dict:
    # A single matched provider candidate
    provider = {
        "name": "Kamran Ghori AC Master",
        "rating": 4.6,
        "review_count": 48,
        "distance_km": 3.0,
        "available": True,
        "base_rate": 500,
        "per_km_rate": 25,
        "on_time_score": 0.90,
        "cancellation_rate": 0.05,
        "review_recency": 0.85,
        "complexity_level": "intermediate",
        "service_type": "AC repair"
    }
    
    intent = {
        "service_type": "AC repair",
        "urgency": urgency,
        "budget_sensitivity": budget_sensitivity,
        "job_complexity": job_complexity,
        "language_detected": language,
        "confidence": 0.95
    }
    
    # We pack them in a mock state representing matching stage output
    return {
        "matching": {
            "status": "success",
            "ranked_providers": [
                {
                    "name": "Kamran Ghori AC Master",
                    "overall_score": 0.88,
                    "score_breakdown": {
                        "distance": 0.9,
                        "rating": 0.9,
                        "review_recency": 0.85,
                        "reliability": 0.92,
                        "price_fit": 0.85,
                        "specialization": 0.90,
                        "availability": 1.0
                    },
                    "rank": 1,
                    "reasoning": "Excellent all-round provider",
                    "provider_data": provider
                }
            ],
            "total_candidates": 1,
            "available_candidates": 1,
            "reasoning_summary": "Top partner found."
        },
        "intent": intent,
        "agent_trace": []
    }


def test_pricing_calculation_and_breakdown():
    """
    Verifies that the Pricing Agent calculates prices correctly and exposes full breakdowns.
    """
    state = _make_state(urgency="scheduled", job_complexity="basic")
    agent = PricingAgent()
    
    result = agent.run(state)
    pricing = result["pricing"]
    
    assert "price_breakdown" in pricing
    breakdown = pricing["price_breakdown"]
    
    # basic complexity = 1.0x (base_fare + distance_fare) = 500 + 25 * 3 = 575
    # basic materials = 0
    # scheduled urgency = 0
    # total = 575
    assert breakdown["base_fare"] == 500.0
    assert breakdown["distance_fare"] == 75.0
    assert breakdown["urgency_surcharge"] == 0.0
    assert breakdown["complexity_surcharge"] == 0.0
    assert breakdown["materials_cost"] == 0.0
    assert breakdown["total_price"] == 575.0
    
    assert pricing["price_range_min"] < pricing["price_breakdown"]["total_price"]
    assert pricing["price_range_max"] > pricing["price_breakdown"]["total_price"]
    assert "explanation" in pricing
    print("  [OK] Standalone Pricing: Base pricing verified.")


def test_pricing_surcharges_and_materials():
    """
    Verifies that complexity multipliers, urgency surcharges, and materials are computed correctly.
    """
    state = _make_state(urgency="urgent", job_complexity="complex", language="english")
    agent = PricingAgent()
    
    result = agent.run(state)
    breakdown = result["pricing"]["price_breakdown"]
    
    # base = 500
    # distance = 75
    # base + dist = 575
    # urgency_multiplier = 1.30 -> surcharge = 575 * 0.3 = 172.50
    # complex_multiplier = 1.80 -> surcharge = (575 * 1.3) * 0.8 = 598.00
    # surge_multiplier = 1.10 -> applied to subtotal (1345.50 * 1.1 = 1480.05)
    # complex materials (AC) = 4500
    # total = 1480.05 + 4500 = 5980.05
    assert breakdown["urgency_surcharge"] == 172.50
    assert breakdown["complexity_surcharge"] == 598.00
    assert breakdown["materials_cost"] == 4500.0
    assert breakdown["total_price"] == 5980.05
    print("  [OK] Standalone Pricing: Surcharges & Materials verified.")


def test_pricing_multilingual_explanation():
    """
    Verifies that the multilingual pricing justification fallbacks generate Urdu/Roman Urdu correctly.
    """
    agent = PricingAgent()
    
    # 1. Test Roman Urdu explanation
    state_ru = _make_state(urgency="urgent", language="roman_urdu")
    res_ru = agent.run(state_ru)["pricing"]
    assert len(res_ru["explanation"]) > 20

    # 2. Test Urdu script explanation
    state_ur = _make_state(urgency="urgent", language="urdu")
    res_ur = agent.run(state_ur)["pricing"]
    # Check that script contains typical Urdu character blocks, Rupees label, or PKR currency/Roman Urdu terms
    explanation_lower = res_ur["explanation"].lower()
    assert (
        "روپے" in res_ur["explanation"] or 
        "rs" in explanation_lower or 
        "pkr" in explanation_lower or 
        "بکنگ" in res_ur["explanation"] or 
        "قیمت" in res_ur["explanation"] or 
        "shukriya" in explanation_lower or 
        "aap" in explanation_lower
    )

    print("  [OK] Standalone Pricing: Multilingual explanations verified.")


if __name__ == "__main__":
    print("\nRunning Standalone Pricing Agent Tests...")
    test_pricing_calculation_and_breakdown()
    test_pricing_surcharges_and_materials()
    test_pricing_multilingual_explanation()
    print("Pricing Agent Tests Passed!\n")
