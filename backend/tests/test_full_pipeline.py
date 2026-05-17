"""
End-to-End Integration Tests for the ServisAI 6-Agent Orchestrator Pipeline.
"""

import sys
import os

# Allow running from either backend/ or project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.pipeline import PipelineOrchestrator


def test_full_pipeline_success_lifecycle():
    """
    Verifies that the entire 6-agent pipeline runs end-to-end successfully.
    Chains: Intent -> Discovery -> Matching -> Pricing -> Booking -> Quality.
    """
    # Multilingual Roman Urdu request
    message = "AC bilkul kaam nahi kar raha, urgent technician chahiye G-13 Islamabad mein. cheap rate ho."
    
    orchestrator = PipelineOrchestrator()
    
    # Run the full end-to-end lifecycle simulation
    # 15:00 is an ODD hour -> Booking will confirm successfully
    # Rating 5 -> Reputation will update successfully
    result = orchestrator.run_full_simulation(
        message=message,
        appointment_time="2026-05-18 15:00",
        rating=5,
        review_text="Bohat hi shandar kaam kiya Ali AC Services ne. Shanti se kaam ho gaya.",
        issue_reported=False
    )
    
    # ── Verify States ──
    assert "intent" in result
    assert result["intent_status"] == "intent_extracted"
    assert result["intent"]["urgency"] == "urgent"
    assert result["intent"]["budget_sensitivity"] == "high"
    
    assert "discovery" in result
    assert result["discovery"]["status"] == "providers_found" or result["discovery"]["status"] == "no_providers"
    
    assert "matching" in result
    assert result["matching"]["status"] == "success" or result["matching"]["status"] == "fallback"
    
    assert "pricing" in result
    assert result["pricing"]["price_breakdown"]["total_price"] > 0
    
    assert "booking" in result
    assert result["booking"]["status"] == "confirmed"
    assert result["booking"]["booking_id"] is not None
    
    assert "quality" in result
    assert result["quality"]["status"] == "reputation_updated"
    assert result["quality"]["review_sentiment"] == "positive"
    
    # ── Verify Traces ──
    traces = result["agent_trace"]
    steps_tracked = [t["step"] for t in traces]
    
    # Check that all stages emitted valid traces
    for step in ["intent", "discovery", "matching", "pricing", "booking", "quality"]:
        assert step in steps_tracked, f"Pipeline missing trace for stage: {step}"
        
    # Check trace contract validity for all traces
    for trace in traces:
        for field in ["step", "agent_name", "input", "output", "tool_called", "duration_ms", "status", "reasoning_summary"]:
            assert field in trace, f"Trace {trace['step']} missing required contract field: {field}"
            
    print("\n  [OK] E2E Full Simulation: Successful 6-Agent transition verified!")


def test_full_pipeline_conflict_lifecycle():
    """
    Verifies that scheduling conflicts trigger fallback slot/provider suggestion logic.
    """
    message = "Hamare bathroom ka flush leak ho raha hai, pani bahar a raha hai. Urgent plumber chahiye F-10 sector Islamabad mein."
    orchestrator = PipelineOrchestrator()
    
    # 14:00 is an EVEN hour -> Booking will trigger a scheduling conflict
    # Rating 1 -> Quality will trigger a dispute escalation
    result = orchestrator.run_full_simulation(
        message=message,
        appointment_time="2026-05-18 14:00",
        rating=1,
        review_text="Chor provider badtameezi ki aur paise le kar chala gaya.",
        issue_reported=True
    )
    
    assert "booking" in result
    assert result["booking"]["status"] == "conflict"
    assert len(result["booking"]["alternative_slots"]) == 2
    
    assert "quality" in result
    assert result["quality"]["status"] == "dispute_escalated"
    assert result["quality"]["review_sentiment"] == "negative"
    
    # Check that disputes escalations trigger warnings/suspensions actions
    assert any("suspension" in act or "suspend" in act or "flagged" in act for act in result["quality"]["actions_taken"])
    
    print("  [OK] E2E Full Simulation: Collision & dispute escalation pathways verified!")


if __name__ == "__main__":
    print("\nRunning End-to-End Orchestrator Pipeline Tests...")
    test_full_pipeline_success_lifecycle()
    test_full_pipeline_conflict_lifecycle()
    print("E2E Orchestrator Tests Passed!\n")
