"""
Tests for the Matching Agent (Agent 3).

Five test cases:
  TC-01  Normal ranking          — 4 available providers, standard intent
  TC-02  Budget-sensitive user   — high budget_sensitivity, cheaper wins
  TC-03  Urgent request          — distance + reliability weights boosted
  TC-04  No available providers  — all unavailable → fallback
  TC-05  Single provider         — only one candidate → fallback

Run from the backend/ directory:
    python -m pytest tests/test_matching_agent.py -v
or directly:
    python tests/test_matching_agent.py
"""

import sys
import os

# Allow running from either backend/ or project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.matching_agent import MatchingAgent

# ─── Shared fixture helpers ────────────────────────────────────────────────

def _make_provider(
    name: str,
    rating: float = 4.0,
    review_count: int = 50,
    distance_km: float = 3.0,
    available: bool = True,
    base_rate: int = 500,
    per_km_rate: int = 25,
    on_time_score: float = 0.85,
    cancellation_rate: float = 0.10,
    review_recency: float = 0.80,
    complexity_level: str = "intermediate",
) -> dict:
    return {
        "name": name,
        "rating": rating,
        "review_count": review_count,
        "distance_km": distance_km,
        "available": available,
        "base_rate": base_rate,
        "per_km_rate": per_km_rate,
        "on_time_score": on_time_score,
        "cancellation_rate": cancellation_rate,
        "review_recency": review_recency,
        "complexity_level": complexity_level,
        "service_type": "AC repair",
        "source": "mock",
    }


def _make_intent(
    urgency: str = "scheduled",
    budget_sensitivity: str = "medium",
    job_complexity: str = "intermediate",
) -> dict:
    return {
        "service_type": "AC repair",
        "urgency": urgency,
        "budget_sensitivity": budget_sensitivity,
        "job_complexity": job_complexity,
        "user_preferences": [],
        "constraints": [],
    }


# ─── Tests ─────────────────────────────────────────────────────────────────

def test_tc01_normal_ranking():
    """
    TC-01: Standard ranking with 4 available providers.
    Expectations:
      - status == "success"
      - 3–5 providers ranked
      - Highest-rated/closest provider is ranked #1
      - Every ranked provider has overall_score > 0
      - Trace has required fields
    """
    providers = [
        _make_provider("Alpha Pro",    rating=4.8, distance_km=1.5, on_time_score=0.95),
        _make_provider("Beta Works",   rating=4.2, distance_km=4.0, on_time_score=0.78),
        _make_provider("Gamma Fix",    rating=3.9, distance_km=6.0, on_time_score=0.82),
        _make_provider("Delta Services", rating=4.5, distance_km=3.0, on_time_score=0.88),
    ]
    intent = _make_intent()

    state = {"providers": providers, "intent": intent, "agent_trace": []}
    agent = MatchingAgent()
    result = agent.run(state)

    matching = result["matching"]

    assert matching["status"] == "success", f"Expected success, got {matching['status']}"
    assert len(matching["ranked_providers"]) >= 3, "Should return at least 3 ranked providers"
    assert len(matching["ranked_providers"]) <= 5, "Should return at most 5 providers"

    # Verify rank ordering
    scores = [p["overall_score"] for p in matching["ranked_providers"]]
    assert scores == sorted(scores, reverse=True), "Providers should be sorted by score descending"

    # All scored providers should be available (score > 0)
    for p in matching["ranked_providers"]:
        assert p["overall_score"] > 0.0, f"{p['name']} has 0 score but was ranked"
        assert p["rank"] >= 1

    # Trace contract
    trace = matching["trace"]
    for field in ["step", "agent_name", "input", "output", "tool_called", "duration_ms", "status", "reasoning_summary"]:
        assert field in trace, f"Trace missing required field: {field}"

    assert trace["step"] == "matching"
    assert trace["agent_name"] == "MatchingAgent"
    assert trace["tool_called"] == "multi_factor_scoring"
    assert trace["status"] == "success"

    # Shared trace list should have entry appended
    assert len(result["agent_trace"]) == 1

    print(f"  ✓ TC-01 PASSED — Top provider: {matching['ranked_providers'][0]['name']} "
          f"(score {matching['ranked_providers'][0]['overall_score']:.4f})")


def test_tc02_budget_sensitive():
    """
    TC-02: High budget_sensitivity → cheapest provider should rise.
    Expectations:
      - status == "success"
      - The cheapest provider (low base_rate) ranks higher than expensive ones
      - score_breakdown.price_fit is highest for the cheapest provider
    """
    providers = [
        _make_provider("Budget King",   rating=3.8, distance_km=4.0, base_rate=300, per_km_rate=15),
        _make_provider("Mid Ranger",    rating=4.3, distance_km=3.5, base_rate=500, per_km_rate=25),
        _make_provider("Premium Pro",   rating=4.9, distance_km=2.0, base_rate=800, per_km_rate=40),
        _make_provider("Average Joe",   rating=4.0, distance_km=5.0, base_rate=450, per_km_rate=20),
    ]
    intent = _make_intent(budget_sensitivity="high")

    state = {"providers": providers, "intent": intent}
    agent = MatchingAgent()
    result = agent.run(state)

    matching = result["matching"]
    assert matching["status"] == "success"

    # Budget King should have the highest price_fit score
    ranked = matching["ranked_providers"]
    price_fits = {p["name"]: p["score_breakdown"]["price_fit"] for p in ranked}

    assert price_fits.get("Budget King", 0) > price_fits.get("Premium Pro", 1), (
        "Budget King should have higher price_fit than Premium Pro for high budget sensitivity"
    )

    print(f"  ✓ TC-02 PASSED — Budget King price_fit: {price_fits.get('Budget King'):.4f} "
          f"vs Premium Pro: {price_fits.get('Premium Pro'):.4f}")


def test_tc03_urgent_request():
    """
    TC-03: Urgent request → distance and reliability weights boosted.
    Expectations:
      - status == "success"
      - The closest + most reliable provider ranks #1
      - Distance and reliability score_breakdown values are high for rank-1
    """
    providers = [
        # Nearby but so-so reliability
        _make_provider("Close Crew",    rating=4.0, distance_km=0.8,
                       on_time_score=0.75, cancellation_rate=0.20),
        # Far but very reliable
        _make_provider("Reliable Remote", rating=4.7, distance_km=12.0,
                       on_time_score=0.98, cancellation_rate=0.02),
        # Nearby AND reliable — should win for urgent
        _make_provider("Quick Reliable", rating=4.5, distance_km=1.2,
                       on_time_score=0.96, cancellation_rate=0.03),
        # Far and unreliable
        _make_provider("Slow Far",      rating=3.5, distance_km=15.0,
                       on_time_score=0.60, cancellation_rate=0.30),
    ]
    intent = _make_intent(urgency="urgent")

    state = {"providers": providers, "intent": intent}
    agent = MatchingAgent()
    result = agent.run(state)

    matching = result["matching"]
    assert matching["status"] == "success"

    top = matching["ranked_providers"][0]

    # For urgent: Quick Reliable (close + reliable) should beat Reliable Remote (far)
    assert top["name"] == "Quick Reliable", (
        f"Expected 'Quick Reliable' as top for urgent, got '{top['name']}'"
    )

    # Distance score should be high for top pick (within 2 km)
    assert top["score_breakdown"]["distance"] > 0.8, (
        f"Top provider's distance score should be high for urgent. Got {top['score_breakdown']['distance']}"
    )

    print(f"  ✓ TC-03 PASSED — Urgent top pick: {top['name']} "
          f"(distance_score={top['score_breakdown']['distance']:.4f}, "
          f"reliability={top['score_breakdown']['reliability']:.4f})")


def test_tc04_no_available_providers():
    """
    TC-04: All providers are unavailable → fallback status, empty ranked list.
    Expectations:
      - status == "fallback"
      - ranked_providers == []
      - available_candidates == 0
      - reasoning_summary mentions unavailability
    """
    providers = [
        _make_provider("Busy Ali",    available=False),
        _make_provider("On Leave",    available=False),
        _make_provider("Closed Shop", available=False),
    ]
    intent = _make_intent()

    state = {"providers": providers, "intent": intent}
    agent = MatchingAgent()
    result = agent.run(state)

    matching = result["matching"]
    assert matching["status"] == "fallback", f"Expected fallback, got {matching['status']}"
    assert matching["ranked_providers"] == [], "Ranked list should be empty when all unavailable"
    assert matching["available_candidates"] == 0
    assert matching["total_candidates"] == 3

    trace = matching["trace"]
    assert trace["status"] == "fallback"
    assert "unavailable" in matching["reasoning_summary"].lower(), (
        "reasoning_summary should mention unavailability"
    )

    print(f"  ✓ TC-04 PASSED — status=fallback, reasoning: '{matching['reasoning_summary']}'")


def test_tc05_single_provider():
    """
    TC-05: Only one provider exists → fallback (below threshold of 2 ranked available).
    Expectations:
      - status == "fallback"
      - ranked_providers has 1 entry (the single available provider IS scored)
      - total_candidates == 1
    """
    providers = [
        _make_provider("Solo Star", rating=4.9, distance_km=2.0,
                       on_time_score=0.95, cancellation_rate=0.04),
    ]
    intent = _make_intent()

    state = {"providers": providers, "intent": intent}
    agent = MatchingAgent()
    result = agent.run(state)

    matching = result["matching"]
    assert matching["status"] == "fallback", (
        f"Expected fallback for single provider, got {matching['status']}"
    )
    assert matching["total_candidates"] == 1

    # The single available provider should still appear in ranked list (scored)
    assert len(matching["ranked_providers"]) == 1, (
        "Single provider should still be scored even in fallback mode"
    )
    assert matching["ranked_providers"][0]["name"] == "Solo Star"
    assert matching["ranked_providers"][0]["overall_score"] > 0.0

    trace = matching["trace"]
    assert trace["status"] == "fallback"

    print(f"  ✓ TC-05 PASSED — status=fallback, single provider scored: "
          f"{matching['ranked_providers'][0]['name']} "
          f"(score={matching['ranked_providers'][0]['overall_score']:.4f})")


# ─── Runner ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n══════════════════════════════════════════════")
    print("  ServisAI — Matching Agent Test Suite")
    print("══════════════════════════════════════════════\n")

    tests = [
        ("TC-01  Normal ranking",         test_tc01_normal_ranking),
        ("TC-02  Budget-sensitive user",  test_tc02_budget_sensitive),
        ("TC-03  Urgent request",         test_tc03_urgent_request),
        ("TC-04  No available providers", test_tc04_no_available_providers),
        ("TC-05  Single provider",        test_tc05_single_provider),
    ]

    passed = 0
    failed = 0

    for label, fn in tests:
        print(f"Running {label}...")
        try:
            fn()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED — {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR  — {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\n══════════════════════════════════════════════")
    print(f"  Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print(f"══════════════════════════════════════════════\n")

    sys.exit(0 if failed == 0 else 1)
