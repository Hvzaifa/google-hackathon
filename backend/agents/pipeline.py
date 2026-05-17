"""
Pipeline Orchestrator — The core orchestration layer of ServisAI.

Chains the entire 6-agent lifecycle:
  Intent ──> Discovery ──> Matching ──> Pricing ──> Booking ──> Quality/Dispute

Uses standard pipeline state passing. Can execute a full lifecycle simulation
or manage selective step transitions with comprehensive trace logs.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

from agents.intent_agent import IntentAgent
from agents.discovery_agent import DiscoveryAgent
from agents.matching_agent import MatchingAgent
from agents.pricing_agent import PricingAgent
from agents.booking_agent import BookingAgent
from agents.quality_agent import QualityAgent
from utils.trace import make_trace


class PipelineOrchestrator:
    """
    An orchestrator that coordinates the state transition and execution sequence of all 6 agents.
    Provides detailed trace logs showing Vertex AI Agent Builder orchestration reasoning at each stage.
    """

    name: str = "PipelineOrchestrator"

    def __init__(self):
        self.intent_agent = IntentAgent()
        self.discovery_agent = DiscoveryAgent()
        self.matching_agent = MatchingAgent()
        self.pricing_agent = PricingAgent()
        self.booking_agent = BookingAgent()
        self.quality_agent = QualityAgent()

    def run_pipeline(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the agents sequentially based on the current active state.
        Allows step-by-step state continuation.
        """
        # Ensure trace aggregator is present
        if "agent_trace" not in state:
            state["agent_trace"] = []

        # ── 1. Intent Extraction ──────────────────────────────────────────
        if "intent" not in state and "user_message" in state:
            print("[Vertex AI Agent Builder Orchestrator] Step 1: Parsing user message intent...")
            state = self.intent_agent.run(state)
                
            if state.get("intent_status") == "clarification_needed":
                print("[Vertex AI Agent Builder Orchestrator] Intent clarification required. Stopping pipeline.")
                return state

        # Check intent is successfully populated
        intent = state.get("intent", {})
        if not intent or intent.get("confidence", 0) < 0.8:
            print("[Vertex AI Agent Builder Orchestrator] Missing or low-confidence intent. Stopping.")
            return state

        # ── 2. Provider Discovery ─────────────────────────────────────────
        if "discovery" not in state:
            print("[Vertex AI Agent Builder Orchestrator] Step 2: Running provider discovery on Maps...")
            state = self.discovery_agent.run(state)

        # Stop if no providers found
        if state.get("discovery", {}).get("status") == "no_providers" or not state.get("providers"):
            print("[Vertex AI Agent Builder Orchestrator] No providers found in vicinity. Stopping.")
            return state

        # ── 3. Multi-Factor Matching ──────────────────────────────────────
        if "matching" not in state:
            print("[Vertex AI Agent Builder Orchestrator] Step 3: Scoring & ranking provider candidates...")
            state = self.matching_agent.run(state)

        # Stop if matching fell back with no candidates
        matching = state.get("matching", {})
        if not matching.get("ranked_providers"):
            print("[Vertex AI Agent Builder Orchestrator] Matching failed to rank candidates. Stopping.")
            return state

        # ── 4. Dynamic Pricing Surcharges ─────────────────────────────────
        if "pricing" not in state:
            print("[Vertex AI Agent Builder Orchestrator] Step 4: Estimating dynamic price quote...")
            state = self.pricing_agent.run(state)

        if state.get("pricing", {}).get("status") == "error":
            print("[Vertex AI Agent Builder Orchestrator] Pricing estimation encountered an error. Stopping.")
            return state

        # ── 4.5. Payment Processing ───────────────────────────────────────
        if "payment" not in state and "pricing" in state:
            print("[Vertex AI Agent Builder Orchestrator] Step 4.5: Processing payment gateway...")
            from tools.payment_tool import simulate_payment, retry_payment_with_cod
            import time
            booking_id_temp = f"BK-PRE-{int(time.time())}"
            total_price = state["pricing"].get("price_breakdown", {}).get("total_price", 0.0)
            
            pay_status, pay_details = simulate_payment(booking_id_temp, total_price)
            
            if pay_status == "payment_failed":
                print(f"[Vertex AI Agent Builder Orchestrator] Payment failed ({pay_details.get('failure_reason')}). Retrying with COD fallback...")
                pay_status, pay_details = retry_payment_with_cod(booking_id_temp, total_price)
                print("[Vertex AI Agent Builder Orchestrator] COD fallback successful.")
            
            state["payment"] = pay_details

        # ── 5. Appointment Booking Check ──────────────────────────────────
        if "booking" not in state and "booking_request" in state:
            print("[Vertex AI Agent Builder Orchestrator] Step 5: Checking slot schedule collision...")
            state = self.booking_agent.run(state)

        # ── 6. Quality Reviews & Reputation Updates ────────────────────────
        if "quality" not in state and "quality_request" in state:
            print("[Vertex AI Agent Builder Orchestrator] Step 6: Processing customer review and reputation update...")
            state = self.quality_agent.run(state)

        print("[Vertex AI Agent Builder Orchestrator] Pipeline executed successfully.")
        return state

    def run_full_simulation(
        self,
        message: str,
        appointment_time: str = "2026-05-18 15:00",
        rating: int = 5,
        review_text: str = "Kamran sahib ne bohat acha aur jaldi kaam kiya. Highly recommended!",
        issue_reported: bool = False,
        use_gemini: bool = False
    ) -> Dict[str, Any]:
        """
        Executes a complete 6-agent simulation in a single run.
        Uses default positive confirmations for Booking and Quality reviews.
        """
        print(f"\n======================================================================")
        print(f"[Vertex AI Agent Builder Orchestrator] STARTING FULL LIFECYCLE SIMULATION")
        print(f"User Message: '{message}'")
        print(f"======================================================================\n")

        # Create initial state
        state = {
            "user_message": message,
            "agent_trace": [],
            "use_gemini": use_gemini
        }

        # Run Intent -> Discovery -> Matching -> Pricing
        state = self.run_pipeline(state)
        
        # Check if pipeline got halted at intent or discovery
        if "pricing" not in state or state["pricing"].get("status") == "error":
            print("[Vertex AI Agent Builder Orchestrator] Pipeline halted early. Returning current state.")
            return state

        # 2. Inject Booking Request Confirmation
        print("\n[Vertex AI Agent Builder Orchestrator] Injecting user booking request confirmation...")
        state["booking_request"] = {
            "appointment_time": appointment_time,
            "user_confirmed": True
        }
        
        # Run Booking Agent
        state = self.run_pipeline(state)

        if "booking" not in state or state["booking"].get("status") == "error":
            return state

        # 3. Inject Post-Service Customer Feedback (Quality review)
        booking_id = state["booking"].get("booking_id") or "BK-SIMULATED"
        print(f"\n[Vertex AI Agent Builder Orchestrator] Injecting customer review for Booking {booking_id}...")
        state["quality_request"] = {
            "booking_id": booking_id,
            "rating": rating,
            "review_text": review_text,
            "issue_reported": issue_reported
        }
        
        # Run Quality Agent
        state = self.run_pipeline(state)

        print(f"\n======================================================================")
        print(f"[Vertex AI Agent Builder Orchestrator] SIMULATION LIFECYCLE COMPLETE")
        print(f"======================================================================\n")
        return state
