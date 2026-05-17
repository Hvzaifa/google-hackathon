from fastapi import FastAPI
from pydantic import BaseModel
import time
from services.intent_runner import run_intent_agent
from agents.discovery_agent import DiscoveryAgent
from agents.matching_agent import MatchingAgent
from agents.pricing_agent import PricingAgent
from utils.trace import make_trace
from orchestration.service_pipeline import service_pipeline


app = FastAPI(title="Hackathon Intent Runner")
discovery_agent = DiscoveryAgent()
matching_agent = MatchingAgent()
pricing_agent = PricingAgent()

class IntentRequest(BaseModel):
    message: str
    user_id: str = "anonymous"


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/intent")
def intent_endpoint(body: IntentRequest):
    return run_intent_agent(body.message)


@app.post("/api/test-discovery")
def test_discovery(body: IntentRequest):
    intent_result = run_intent_agent(body.message)

    if intent_result["status"] == "clarification_needed":
        return intent_result

    state = {
        "user_message": body.message,
        "intent": intent_result["intent"]
    }

    start = time.time()
    state = discovery_agent.run(state)

    discovery_trace = make_trace(
        step_name="discovery",
        input_data=state["intent"],
        output_data=state["discovery"],
        tool_called=(
            "mock_provider_dataset"
            if state["discovery"].get("fallback_used")
            else "google_maps_geocoding_api + google_maps_places_api"
        ),
        start_time=start,
    )

    return {
        "status": state["discovery"]["status"],
        "intent": state["intent"],
        "discovery": state["discovery"],
        "agent_trace": intent_result["agent_trace"] + [discovery_trace]
    }


@app.post("/api/test-matching")
def test_matching(body: IntentRequest):

    intent_result = run_intent_agent(body.message)

    if intent_result["status"] == "clarification_needed":
        return intent_result

    state = {
        "user_message": body.message,
        "intent": intent_result["intent"]
    }

    # Discovery
    discovery_start = time.time()

    state = discovery_agent.run(state)

    discovery_trace = make_trace(
        step_name="discovery",
        input_data=state["intent"],
        output_data=state["discovery"],
        tool_called=(
            "mock_provider_dataset"
            if state["discovery"].get("fallback_used")
            else "google_maps_geocoding_api + google_maps_places_api"
        ),
        start_time=discovery_start,
    )

    # Matching
    matching_start = time.time()

    state = matching_agent.run(state)

    matching_trace = make_trace(
        step_name="matching",
        input_data={
            "providers_count": len(state.get("providers", [])),
            "intent": state["intent"]
        },
        output_data=state["matching"],
        tool_called="weighted_provider_ranking_algorithm",
        start_time=matching_start,
    )

    return {
        "status": state["matching"]["status"],
        "intent": state["intent"],
        "discovery": state["discovery"],
        "matching": state["matching"],
        "agent_trace": (
            intent_result["agent_trace"]
            + [discovery_trace]
            + [matching_trace]
        )
    }


@app.post("/api/test-pricing")
def test_pricing(body: IntentRequest):

    intent_result = run_intent_agent(body.message)

    if intent_result["status"] == "clarification_needed":
        return intent_result

    state = {
        "user_message": body.message,
        "intent": intent_result["intent"]
    }

    # Discovery
    discovery_start = time.time()
    state = discovery_agent.run(state)

    discovery_trace = make_trace(
        step_name="discovery",
        input_data=state["intent"],
        output_data=state["discovery"],
        tool_called=(
            "mock_provider_dataset"
            if state["discovery"].get("fallback_used")
            else "google_maps_geocoding_api + google_maps_places_api"
        ),
        start_time=discovery_start,
    )

    if state["discovery"]["status"] == "no_providers":
        return {
            "status": "no_providers",
            "intent": state["intent"],
            "discovery": state["discovery"],
            "agent_trace": intent_result["agent_trace"] + [discovery_trace],
        }

    # Matching
    matching_start = time.time()
    state = matching_agent.run(state)

    matching_trace_output = {
        "status": state["matching"]["status"],
        "selected_provider": state["matching"]["selected_provider"]["name"],
        "matching_score": state["matching"]["selected_provider"]["final_matching_score"],
        "decision_factors": state["matching"]["decision_factors"],
        "summary": state["matching"]["ranking_summary"],
    }

    matching_trace = make_trace(
        step_name="matching",
        input_data={
            "providers_count": len(state.get("providers", [])),
            "intent": state["intent"],
        },
        output_data=matching_trace_output,
        tool_called="weighted_provider_ranking_algorithm",
        start_time=matching_start,
    )

    # Pricing
    pricing_start = time.time()
    state = pricing_agent.run(state)

    pricing_trace_output = {
        "status": state["pricing"]["status"],
        "provider_name": state["pricing"]["provider_name"],
        "price": state["pricing"]["price"],
        "price_range": state["pricing"]["price_range"],
        "decision_factors": state["pricing"]["decision_factors"],
        "summary": state["pricing"]["pricing_summary"],
    }

    pricing_trace = make_trace(
        step_name="pricing",
        input_data={
            "selected_provider": state.get("selected_provider", {}).get("name"),
            "intent": state["intent"],
        },
        output_data=pricing_trace_output,
        tool_called="adk_pricing_agent + calculate_service_price_tool",
        start_time=pricing_start,
    )

    return {
        "status": state["pricing"]["status"],
        "intent": state["intent"],
        "discovery": state["discovery"],
        "matching": state["matching"],
        "pricing": state["pricing"],
        "agent_trace": (
            intent_result["agent_trace"]
            + [discovery_trace]
            + [matching_trace]
            + [pricing_trace]
        ),
    }


@app.post("/api/orchestrate")
def orchestrate(body: IntentRequest):

    initial_state = {
        "user_message": body.message,
        "user_id": body.user_id,
        "agent_trace": [],
    }

    final_state = service_pipeline.run(initial_state)

    return {
        "pipeline_status": final_state.get("pipeline_status"),

        "intent": final_state.get("intent"),

        "discovery": final_state.get("discovery"),

        "matching": final_state.get("matching"),

        "pricing": final_state.get("pricing"),

        "booking": final_state.get("booking"),

        "lifecycle": final_state.get("lifecycle"),

        "agent_trace": final_state.get("agent_trace"),
    }