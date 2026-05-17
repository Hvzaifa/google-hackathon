"""
Standalone tests for the Quality and Dispute Agent.
"""

import sys
import os

# Allow running from either backend/ or project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.quality_agent import QualityAgent


def _make_state(
    rating: int = 5,
    review_text: str = "Acha kaam kiya",
    issue_reported: bool = False,
    language: str = "roman_urdu"
) -> dict:
    booking = {
        "booking_id": "BK-98765",
        "provider_name": "Ali AC Services",
        "appointment_time": "2026-05-18 15:00",
        "total_price": 1200.0,
        "status": "confirmed"
    }
    
    intent = {
        "service_type": "AC repair",
        "language_detected": language
    }
    
    quality_request = {
        "booking_id": "BK-98765",
        "provider_name": "Ali AC Services",
        "rating": rating,
        "review_text": review_text,
        "issue_reported": issue_reported
    }
    
    # We pack them in a mock state representing booking stage output
    return {
        "booking": booking,
        "intent": intent,
        "quality_request": quality_request,
        "providers": [
            {
                "name": "Ali AC Services",
                "rating": 4.0,
                "review_count": 10,
                "available": True
            }
        ],
        "agent_trace": []
    }


def test_quality_feedback_reputation_update():
    """
    Verifies that rating submissions correctly compute Bayesian updates on the provider reputation.
    """
    # Current: 4.0 rating with 10 reviews. We submit a 5 rating.
    # New: (4.0 * 10 + 5) / 11 = 45 / 11 = 4.09 rating with 11 reviews.
    state = _make_state(rating=5, review_text="Bohot acha kaam kiya, timing perfect thi.", language="roman_urdu")
    agent = QualityAgent()
    
    result = agent.run(state)
    quality = result["quality"]
    
    assert quality["status"] == "reputation_updated"
    assert quality["rating_given"] == 5
    assert quality["new_provider_rating"] == 4.09
    assert quality["new_provider_review_count"] == 11
    
    # Check persistent mutation in the state providers list
    provider_in_state = result["providers"][0]
    assert provider_in_state["rating"] == 4.09
    assert provider_in_state["review_count"] == 11
    
    assert "feedback ka buhat shukriya" in quality["resolution_message"].lower() or "shukriya" in quality["resolution_message"].lower()
    print("  [OK] Standalone Quality: Reputation score Bayesian updates verified.")


def test_quality_minor_dispute_resolution():
    """
    Verifies that minor complaints (late, expensive) issue automated apology coupons.
    """
    state = _make_state(rating=2, review_text="Late aya aur bad me gas leak ho gayi.", language="english")
    agent = QualityAgent()
    
    result = agent.run(state)
    quality = result["quality"]
    
    assert quality["status"] == "dispute_resolved"
    assert any("coupon" in act or "wallet" in act or "apology" in act for act in quality["actions_taken"])
    assert len(quality["resolution_message"]) > 10
    print("  [OK] Standalone Quality: Automated minor dispute coupons verified.")


def test_quality_severe_dispute_escalation():
    """
    Verifies that severe verbal abuse or theft reports automatically trigger human support escalation.
    """
    state = _make_state(rating=1, review_text="Chor hai! Mera mobile chori kar liya.", language="urdu")
    agent = QualityAgent()
    
    result = agent.run(state)
    quality = result["quality"]
    
    assert quality["status"] == "dispute_escalated"
    assert "suspension" in "".join(quality["actions_taken"]).lower() or "suspended" in "".join(quality["actions_taken"]).lower() or "flagged" in "".join(quality["actions_taken"]).lower()
    assert quality["escalation_reason"] is not None
    assert len(quality["resolution_message"]) > 10
    print("  [OK] Standalone Quality: Severe Urdu theft dispute human escalation verified.")


if __name__ == "__main__":
    print("\nRunning Standalone Quality Agent Tests...")
    test_quality_feedback_reputation_update()
    test_quality_minor_dispute_resolution()
    test_quality_severe_dispute_escalation()
    print("Quality Agent Tests Passed!\n")
