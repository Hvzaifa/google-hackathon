import time

from services.intent_runner import run_intent_agent
from agents.discovery_agent import DiscoveryAgent
from agents.matching_agent import MatchingAgent
from agents.pricing_agent import PricingAgent
from agents.booking_agent import BookingAgent
from utils.trace import make_trace
from tools.lifecycle_tool import simulate_booking_lifecycle
from tools.evidence_tool import create_completion_evidence_placeholder
from tools.cancellation_recovery_tool import recover_from_provider_cancellation

discovery_agent = DiscoveryAgent()
matching_agent = MatchingAgent()
pricing_agent = PricingAgent()
booking_agent = BookingAgent()


class ServisAIOrchestrationPipeline:
    """
    Antigravity / Google ADK-style orchestration controller.

    This pipeline centrally manages:
    - agent sequencing
    - shared state propagation
    - tool execution
    - fallback flow
    - trace logging

    Individual LLM agents are defined with Google ADK LlmAgent.
    Deterministic agents are wrapped as orchestration steps.
    """

    name = "ServisAIOrchestrationPipeline"

    def run(self, initial_state: dict) -> dict:
        """
        Full pipeline (backward compat / testing).
        Runs Intent -> Discovery -> Matching -> Pricing -> Booking -> Lifecycle.
        """
        state = self.run_pre_booking(initial_state)

        if state["pipeline_status"] != "awaiting_booking_confirmation":
            return state

        return self.run_booking(state)

    # ────────────────────────────────────────────────────────
    # Phase 1: Pre-Booking (Intent → Discovery → Matching → Pricing)
    # ────────────────────────────────────────────────────────

    def run_pre_booking(self, initial_state: dict) -> dict:
        state = initial_state
        state.setdefault("agent_trace", [])

        # 1. Intent Agent
        intent_result = run_intent_agent(state["user_message"])

        state["intent"] = intent_result["intent"]
        state["pipeline_status"] = intent_result["status"]
        state["agent_trace"].extend(intent_result["agent_trace"])

        if state["pipeline_status"] == "clarification_needed":
            return state

        # 2. Discovery Agent
        discovery_start = time.time()
        flags = state.get("simulation_flags", {})

        if flags.get("simulate_no_providers"):
            state["discovery"] = {
                "status": "no_providers",
                "providers_count": 0,
                "source": "simulation",
                "fallback_used": False,
                "fallback_reason": "Simulated no providers found",
                "providers": [],
            }
            state["providers"] = []
        else:
            state = discovery_agent.run(state)

        discovery_trace_output = {
            "status": state["discovery"]["status"],
            "providers_count": state["discovery"].get("providers_count", 0),
            "source": state["discovery"].get("source"),
            "fallback_used": state["discovery"].get("fallback_used"),
            "fallback_reason": state["discovery"].get("fallback_reason"),
        }

        state["agent_trace"].append(
            make_trace(
                step_name="discovery",
                input_data={
                    "service_type": state["intent"].get("service_type"),
                    "location": state["intent"].get("location"),
                },
                output_data=discovery_trace_output,
                tool_called=(
                    "mock_provider_dataset"
                    if state["discovery"].get("fallback_used")
                    else "google_maps_geocoding_api + google_maps_places_api"
                ),
                start_time=discovery_start,
                trace_type="tool_execution",
            )
        )

        if state["discovery"]["status"] == "no_providers":
            state["pipeline_status"] = "no_providers"
            state["fallback_response"] = {
                "status": "no_providers",
                "message": "No suitable providers found for this request.",
                "alternatives": [
                    "Try a nearby location",
                    "Try a different time",
                    "Expand provider search radius",
                    "Use mock fallback providers for demo"
                ]
            }
            return state

        # 3. Matching Agent
        matching_start = time.time()
        state = matching_agent.run(state)

        selected = state["matching"].get("selected_provider")

        matching_trace_output = {
            "status": state["matching"]["status"],
            "selected_provider": selected.get("name") if selected else None,
            "matching_score": selected.get("final_matching_score") if selected else None,
            "decision_factors": state["matching"].get("decision_factors", []),
            "summary": state["matching"].get("ranking_summary"),
        }

        state["agent_trace"].append(
            make_trace(
                step_name="matching",
                input_data={
                    "providers_count": len(state.get("providers", []))
                },
                output_data=matching_trace_output,
                tool_called="weighted_provider_ranking_algorithm",
                start_time=matching_start,
                trace_type="decision",
            )
        )

        if state["matching"]["status"] != "provider_selected":
            state["pipeline_status"] = state["matching"]["status"]
            return state

        # 4. Pricing Agent
        pricing_start = time.time()
        state = pricing_agent.run(state)

        pricing_trace_output = {
            "status": state["pricing"]["status"],
            "provider_name": state["pricing"].get("provider_name"),
            "price": state["pricing"].get("price"),
            "price_range": state["pricing"].get("price_range"),
            "decision_factors": state["pricing"].get("decision_factors", []),
            "summary": state["pricing"].get("pricing_summary"),
        }

        state["agent_trace"].append(
            make_trace(
                step_name="pricing",
                input_data={
                    "provider": state["pricing"].get("provider_name")
                },
                output_data=pricing_trace_output,
                tool_called="adk_pricing_agent + calculate_service_price_tool",
                start_time=pricing_start,
                trace_type="calculation",
            )
        )

        state["pipeline_status"] = "awaiting_booking_confirmation"

        flags = state.get("simulation_flags", {})

        if flags.get("simulate_payment_failure"):
            state["pipeline_status"] = "payment_confirmation_failed"

            state["payment_fallback"] = {
                "status": "payment_confirmation_failed",
                "message": "Payment confirmation failed. Booking was not finalized.",
                "recommended_action": "Retry payment or switch to cash-on-service."
            }

            state["agent_trace"].append(
                make_trace(
                    step_name="payment_failure",
                    input_data={
                        "price": state["pricing"]["price"]
                    },
                    output_data=state["payment_fallback"],
                    tool_called="payment_confirmation_simulation",
                    start_time=time.time(),
                    trace_type="fallback",
                )
            )

        return state

    # ────────────────────────────────────────────────────────
    # Phase 2: Booking (Booking → Evidence → Lifecycle)
    # Called ONLY after user confirms via /api/book
    # ────────────────────────────────────────────────────────

    def run_booking(self, state: dict) -> dict:
        state.setdefault("agent_trace", [])

        # 5. Booking Agent
        booking_start = time.time()

        state = booking_agent.run(state)

        booking_trace_output = {
            "status": state["booking"]["status"],
            "booking_id": state["booking"].get("booking_id"),
            "booking_status": state["booking"].get(
                "booking_status"
            ),
            "eta_minutes": state["booking"].get(
                "estimated_eta_minutes"
            ),
            "database_inserted": state["booking"].get(
                "database_inserted"
            ),
            "scheduling": state["booking"].get("scheduling"),
            "summary": state["booking"].get(
                "booking_summary"
            ),
        }

        state["agent_trace"].append(
            make_trace(
                step_name="booking",
                input_data={
                    "provider": state["selected_provider"]["name"],
                    "price": state["pricing"]["price"],
                },
                output_data=booking_trace_output,
                tool_called=(
                    "adk_booking_agent + "
                    "supabase_booking_tool"
                ),
                start_time=booking_start,
                trace_type="worflow_execution",
            )
        )

        state["pipeline_status"] = "booking_confirmed"

        if state["booking"]["status"] == "booking_pending_local_fallback":
            state["pipeline_status"] = "booking_pending_local_fallback"
            return state

        if state["booking"]["booking_status"] == "pending_reschedule":
            state["pipeline_status"] = "pending_reschedule"
            return state

        evidence_start = time.time()

        state["completion_evidence"] = create_completion_evidence_placeholder(
            booking=state["booking"]
        )

        state["agent_trace"].append(
            make_trace(
                step_name="completion_evidence",
                input_data={
                    "booking_id": state["booking"]["booking_id"]
                },
                output_data=state["completion_evidence"],
                tool_called="service_completion_evidence_placeholder_tool",
                start_time=evidence_start,
                trace_type="workflow_execution",
            )
        )

        flags = state.get("simulation_flags", {})

        if flags.get("simulate_provider_cancellation"):
            cancellation_start = time.time()

            state["cancellation_fallback"] = (
                recover_from_provider_cancellation(state)
            )

            if state["cancellation_fallback"].get("replacement_provider"):
                replacement = state["cancellation_fallback"]["replacement_provider"]

                state["selected_provider"] = replacement

                state["booking"]["provider"] = {
                    "name": replacement.get("name"),
                    "rating": replacement.get("rating"),
                    "distance_km": replacement.get("distance_km"),
                }

                state["booking"]["booking_summary"] = (
                    f"Original provider cancelled. "
                    f"Booking reassigned to {replacement.get('name')}."
                )

                if state["booking"].get("notifications"):
                    state["booking"]["notifications"]["notifications"].append({
                        "booking_id": state["booking"].get("booking_id"),
                        "recipient_type": "user",
                        "channel": "in_app",
                        "title": "Provider reassigned",
                        "message": (
                            f"Original provider cancelled. "
                            f"Your booking has been reassigned to "
                            f"{replacement.get('name')}."
                        ),
                        "status": "simulated",
                        "database_inserted": False,
                    })

            state["pipeline_status"] = state["cancellation_fallback"]["status"]

            state["agent_trace"].append(
                make_trace(
                    step_name="provider_cancellation_recovery",
                    input_data={
                        "cancelled_provider": state["cancellation_fallback"].get(
                            "cancelled_provider"
                        ),
                        "original_booking_id": state.get("booking", {}).get(
                            "booking_id"
                        ),
                    },
                    output_data={
                        "status": state["cancellation_fallback"]["status"],
                        "replacement_provider": (
                            state["cancellation_fallback"]
                            .get("replacement_provider", {})
                            .get("name")
                            if state["cancellation_fallback"].get("replacement_provider")
                            else None
                        ),
                        "database_inserted": state["cancellation_fallback"].get(
                            "database_inserted"
                        ),
                        "message": state["cancellation_fallback"].get("message"),
                    },
                    tool_called="antigravity_provider_cancellation_recovery + waitlist_queue_tool",
                    start_time=cancellation_start,
                    trace_type="fallback",
                )
            )

            return state

        # 6. Lifecycle / Follow-up Simulation
        lifecycle_start = time.time()

        state["lifecycle"] = simulate_booking_lifecycle(
            booking=state["booking"]
        )

        lifecycle_trace_output = {
            "status": state["lifecycle"]["status"],
            "booking_id": state["lifecycle"]["booking_id"],
            "final_status": state["lifecycle"]["final_status"],
            "events_count": len(state["lifecycle"]["events"]),
            "summary": state["lifecycle"]["summary"],
        }

        state["agent_trace"].append(
            make_trace(
                step_name="lifecycle_followup",
                input_data={
                    "booking_id": state["booking"]["booking_id"],
                    "booking_status": state["booking"]["booking_status"],
                },
                output_data=lifecycle_trace_output,
                tool_called=(
                    "antigravity_lifecycle_orchestration + "
                    "supabase_booking_events_tool"
                ),
                start_time=lifecycle_start,
                trace_type="lifecycle"
            )
        )

        state["pipeline_status"] = "lifecycle_completed"

        return state


service_pipeline = ServisAIOrchestrationPipeline()