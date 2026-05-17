"""
Standalone tests for the Booking Agent.
"""

import sys
import os

# Allow running from either backend/ or project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.booking_agent import BookingAgent


def _make_state(
    appointment_time: str,
    language: str = "roman_urdu"
) -> dict:
    pricing = {
        "provider_name": "Rizwan Cooling Center",
        "price_breakdown": {
            "base_fare": 500.0,
            "distance_fare": 100.0,
            "urgency_surcharge": 0.0,
            "complexity_surcharge": 150.0,
            "materials_cost": 1200.0,
            "total_price": 1950.0,
            "currency": "PKR"
        },
        "price_range_min": 1755.0,
        "price_range_max": 2145.0,
        "explanation": "Cost quote explanation"
    }
    
    intent = {
        "service_type": "AC repair",
        "urgency": "scheduled",
        "language_detected": language
    }
    
    booking_request = {
        "appointment_time": appointment_time,
        "user_confirmed": True
    }
    
    # We pack them in a mock state representing matching + pricing stage output
    return {
        "pricing": pricing,
        "intent": intent,
        "booking_request": booking_request,
        "providers": [
            {"name": "Rizwan Cooling Center", "rating": 4.5},
            {"name": "Ali AC Services", "rating": 4.8},
            {"name": "Capital Electric Works", "rating": 4.6}
        ],
        "agent_trace": []
    }


def test_booking_confirmation():
    """
    Verifies that a slot request on an ODD hour leads to successful confirmation.
    """
    # 15:00 is an odd hour (15 % 2 != 0) -> should be confirmed
    state = _make_state(appointment_time="2026-05-18 15:00", language="english")
    agent = BookingAgent()
    
    result = agent.run(state)
    booking = result["booking"]
    
    assert booking["status"] == "confirmed"
    assert booking["booking_id"] is not None
    assert booking["booking_id"].startswith("BK-")
    assert len(booking["reminders_sent"]) > 0
    assert len(booking["progress_updates"]) > 0
    assert "confirmed" in booking["message"].lower()
    print("  [OK] Standalone Booking: Successful confirmation verified.")


def test_booking_conflict():
    """
    Verifies that a slot request on an EVEN hour leads to a conflict and proposes fallbacks.
    """
    # 14:00 is an even hour (14 % 2 == 0) -> should raise conflict
    state = _make_state(appointment_time="2026-05-18 14:00", language="roman_urdu")
    agent = BookingAgent()
    
    result = agent.run(state)
    booking = result["booking"]
    
    assert booking["status"] == "conflict"
    assert booking["booking_id"] is None
    assert len(booking["alternative_slots"]) == 2
    assert len(booking["alternative_providers"]) > 0
    
    # Check that booked provider is excluded from alternatives suggestions
    assert "Rizwan Cooling Center" not in booking["alternative_providers"]
    assert "Ali AC Services" in booking["alternative_providers"]
    
    assert len(booking["message"]) > 10
    print("  [OK] Standalone Booking: Double-booking schedule conflict verified.")


if __name__ == "__main__":
    print("\nRunning Standalone Booking Agent Tests...")
    test_booking_confirmation()
    test_booking_conflict()
    print("Booking Agent Tests Passed!\n")
