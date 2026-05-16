from fastapi import FastAPI
from pydantic import BaseModel
import time
from services.intent_runner import run_intent_agent
from agents.discovery_agent import DiscoveryAgent
from utils.trace import make_trace

app = FastAPI(title="Hackathon Intent Runner")
discovery_agent = DiscoveryAgent()


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
        tool_called="google_maps_places_api_or_mock_fallback",
        start_time=start,
    )

    return {
        "status": state["discovery"]["status"],
        "intent": state["intent"],
        "discovery": state["discovery"],
        "agent_trace": intent_result["agent_trace"] + [discovery_trace]
    }