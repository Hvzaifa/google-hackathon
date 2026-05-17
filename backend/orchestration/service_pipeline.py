import time

from services.intent_runner import run_intent_agent
from agents.discovery_agent import DiscoveryAgent
from agents.matching_agent import MatchingAgent
from agents.pricing_agent import PricingAgent
from agents.booking_agent import BookingAgent
from utils.trace import make_trace
from tools.lifecycle_tool import simulate_booking_lifecycle


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
            )
        )

        if state["discovery"]["status"] == "no_providers":
            state["pipeline_status"] = "no_providers"
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
            )
        )

        state["pipeline_status"] = "price_calculated"

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
            )
        )

        state["pipeline_status"] = "booking_confirmed"

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
            )
        )

        state["pipeline_status"] = "lifecycle_completed"

        return state


service_pipeline = ServisAIOrchestrationPipeline()