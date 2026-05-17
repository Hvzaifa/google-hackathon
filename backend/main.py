from fastapi import FastAPI
from pydantic import BaseModel, Field
import time
from typing import List, Dict, Optional

from services.intent_runner import run_intent_agent
from agents.discovery_agent import DiscoveryAgent
from utils.trace import make_trace

# Import new agent runner services
from services.pricing_runner import run_pricing_agent
from services.booking_runner import run_booking_agent
from services.quality_runner import run_quality_agent
from services.pipeline_runner import run_full_pipeline, run_pipeline_step

app = FastAPI(title="ServisAI Orchestrator API Gateway")
discovery_agent = DiscoveryAgent()


class IntentRequest(BaseModel):
    message: str
    user_id: str = "anonymous"
    use_gemini: bool = Field(default=False, description="Use Google Gemini instead of Groq")


class PricingRequest(BaseModel):
    state: dict = Field(..., description="Pipeline state holding intent and matched provider details")
    use_gemini: bool = Field(default=False, description="Use Google Gemini instead of Groq")


class BookingRequest(BaseModel):
    state: dict = Field(..., description="Pipeline state holding intent, pricing details, and booking_request")
    use_gemini: bool = Field(default=False, description="Use Google Gemini instead of Groq")


class QualityRequest(BaseModel):
    state: dict = Field(..., description="Pipeline state holding intent, booking receipt, and quality_request")
    use_gemini: bool = Field(default=False, description="Use Google Gemini instead of Groq")


class PipelineRequest(BaseModel):
    message: str = Field(..., description="Raw multilingual user service request message")
    appointment_time: str = Field(default="2026-05-18 15:00", description="Desired appointment slot (YYYY-MM-DD HH:MM)")
    rating: int = Field(default=5, ge=1, le=5, description="Simulated service review rating (1-5)")
    review_text: str = Field(default="Bohat acha kaam kiya. Highly recommended!", description="Simulated review text")
    issue_reported: bool = Field(default=False, description="Flag if simulated service issue/dispute is raised")
    use_gemini: bool = Field(default=False, description="Use Google Gemini instead of Groq")


@app.get("/api/health")
def health():
    import os
    import time
    
    # 1. Check LLM status
    groq_api_key_set = bool(os.getenv("GROQ_API_KEY"))
    gemini_api_key_set = bool(os.getenv("GEMINI_API_KEY"))
    
    # 2. Check Google Maps API Key
    maps_key_set = bool(os.getenv("GOOGLE_MAPS_API_KEY"))
    
    # 3. Check mock providers file exists
    from tools.maps_tool import load_mock_providers
    try:
        load_mock_providers("electrician")
        mock_data_ok = True
    except Exception:
        mock_data_ok = False
        
    # 4. Check dynamic pricing math
    from tools.pricing_tool import estimate_materials_cost
    try:
        estimate_materials_cost("plumber", "basic")
        pricing_math_ok = True
    except Exception:
        pricing_math_ok = False

    status = "ok"
    if not (groq_api_key_set or gemini_api_key_set) or not mock_data_ok or not pricing_math_ok:
        status = "degraded"
        
    return {
        "status": status,
        "timestamp": time.time(),
        "services": {
            "groq_llm": "available" if groq_api_key_set else "unavailable",
            "gemini_llm": "available" if gemini_api_key_set else "unavailable",
            "google_maps": "configured" if maps_key_set else "mock_fallback_active",
            "mock_database": "ok" if mock_data_ok else "error",
            "pricing_math": "ok" if pricing_math_ok else "error"
        }
    }


@app.post("/api/intent")
def intent_endpoint(body: IntentRequest):
    res = run_intent_agent(body.message, use_gemini=body.use_gemini)
    res["role"] = "agent"
    res["user_query"] = {"role": "user", "message": body.message}
    return res


@app.post("/api/discovery")
def test_discovery(body: IntentRequest):
    intent_result = run_intent_agent(body.message, use_gemini=body.use_gemini)

    if intent_result["status"] == "clarification_needed":
        intent_result["role"] = "agent"
        intent_result["user_query"] = {"role": "user", "message": body.message}
        return intent_result

    state = {
        "user_message": body.message,
        "intent": intent_result["intent"],
        "use_gemini": body.use_gemini
    }

    state = discovery_agent.run(state)
    discovery_trace = state["discovery"].get("trace")

    return {
        "role": "agent",
        "user_query": {"role": "user", "message": body.message},
        "status": state["discovery"]["status"],
        "intent": state["intent"],
        "discovery": state["discovery"],
        "agent_trace": intent_result.get("agent_trace", []) + ([discovery_trace] if discovery_trace else [])
    }


@app.post("/api/pricing")
def pricing_endpoint(body: PricingRequest):
    """
    Standalone Pricing Agent endpoint.
    Computes exact quotes, surcharges, and localized explanation strings.
    """
    import copy
    original_state = copy.deepcopy(body.state)
    state = body.state
    if body.use_gemini:
        state["use_gemini"] = True
    res = run_pricing_agent(state)
    res["role"] = "agent"
    res["user_query"] = {"role": "user", "state_provided": original_state}
    return res


@app.post("/api/booking")
def booking_endpoint(body: BookingRequest):
    """
    Standalone Booking Agent endpoint.
    Verifies slot collision availability and issues booking receipts.
    """
    import copy
    original_state = copy.deepcopy(body.state)
    state = body.state
    if body.use_gemini:
        state["use_gemini"] = True
    res = run_booking_agent(state)
    res["role"] = "agent"
    res["user_query"] = {"role": "user", "state_provided": original_state}
    return res


@app.post("/api/quality")
def quality_endpoint(body: QualityRequest):
    """
    Standalone Quality/Dispute Agent endpoint.
    Updates provider reputations, runs reviews analysis, and handles disputes.
    """
    import copy
    original_state = copy.deepcopy(body.state)
    state = body.state
    if body.use_gemini:
        state["use_gemini"] = True
    res = run_quality_agent(state)
    res["role"] = "agent"
    res["user_query"] = {"role": "user", "state_provided": original_state}
    return res


@app.post("/api/pipeline")
def pipeline_endpoint(body: PipelineRequest):
    """
    Full end-to-end Pipeline simulation orchestrator endpoint.
    Executes Intent, Discovery, Matching, Pricing, Booking, and Quality agents.
    """
    res = run_full_pipeline(
        message=body.message,
        appointment_time=body.appointment_time,
        rating=body.rating,
        review_text=body.review_text,
        issue_reported=body.issue_reported,
        use_gemini=body.use_gemini
    )
    res["role"] = "agent"
    res["user_query"] = {
        "role": "user",
        "message": body.message,
        "appointment_time": body.appointment_time,
        "rating": body.rating,
        "review_text": body.review_text,
        "issue_reported": body.issue_reported
    }
    return res


# ─── Waitlist, Disputes, and Workload Optimization Endpoints ───

class PromoteRequest(BaseModel):
    provider_name: str
    appointment_time: str


class DisputeRequest(BaseModel):
    booking_id: str
    provider_name: str
    rating: int = 1
    review_text: str = ""
    photo_evidence_urls: List[str] = Field(default_factory=list)
    completion_checklist: Dict[str, bool] = Field(default_factory=dict)
    use_gemini: bool = Field(default=False)


@app.post("/api/waitlist/promote")
def promote_waitlist_endpoint(body: PromoteRequest):
    """Promotes the next user in queue for a provider and appointment time."""
    from tools.waitlist_tool import auto_reschedule_next
    from tools.optimization_tool import record_booking
    
    next_user = auto_reschedule_next(body.provider_name, body.appointment_time)
    if next_user:
        # Log confirmed booking in optimizer
        record_booking(provider_name=body.provider_name, total_price=3000.0) # PKR 3000 default price
        return {
            "status": "promoted",
            "promoted_user": next_user,
            "message": f"User {next_user['user_id']} successfully promoted from waitlist to slot {body.appointment_time}."
        }
    return {
        "status": "empty",
        "message": f"No users queued on waitlist for {body.provider_name} at {body.appointment_time}."
    }


def _handle_dispute_endpoint(body: DisputeRequest, dispute_type: str):
    """Common helper to run quality agent for a specific dispute type."""
    state = {
        "quality_request": {
            "booking_id": body.booking_id,
            "provider_name": body.provider_name,
            "rating": body.rating,
            "review_text": body.review_text,
            "issue_reported": True,
            "dispute_type": dispute_type,
            "photo_evidence_urls": body.photo_evidence_urls,
            "completion_checklist": body.completion_checklist
        },
        "use_gemini": body.use_gemini
    }
    res = run_quality_agent(state)
    res["role"] = "agent"
    res["user_query"] = {
        "role": "user",
        "dispute_type": dispute_type,
        "booking_id": body.booking_id,
        "provider_name": body.provider_name
    }
    return res


@app.post("/api/dispute/no-show")
def dispute_no_show_endpoint(body: DisputeRequest):
    """Handles client report of provider no-show."""
    return _handle_dispute_endpoint(body, "no_show")


@app.post("/api/dispute/cancellation")
def dispute_cancellation_endpoint(body: DisputeRequest):
    """Handles client report of provider cancel/refusal to serve."""
    return _handle_dispute_endpoint(body, "cancellation")


@app.post("/api/dispute/price")
def dispute_price_endpoint(body: DisputeRequest):
    """Handles client dispute over final service charge pricing."""
    return _handle_dispute_endpoint(body, "price_disagreement")


@app.post("/api/dispute/overrun")
def dispute_overrun_endpoint(body: DisputeRequest):
    """Handles client dispute over severe completion overrun / delays."""
    return _handle_dispute_endpoint(body, "overrun")


class EscalationRequest(BaseModel):
    booking_id: str
    provider_name: str
    escalation_reason: str


@app.post("/api/escalation")
def escalation_endpoint(body: EscalationRequest):
    """Human-tier escalation endpoint for severe disputes."""
    return {
        "status": "escalated_to_human",
        "ticket_id": f"TKT-{body.booking_id}",
        "message": f"Escalated booking {body.booking_id} for {body.provider_name} to operations desk.",
        "reason": body.escalation_reason
    }


@app.get("/api/optimization")
def optimization_endpoint():
    """Returns opportunity fairness metrics and workload booking history."""
    from tools.optimization_tool import get_opportunity_fairness_index, _booking_history
    return {
        "opportunity_fairness_index": get_opportunity_fairness_index(),
        "booking_history": _booking_history
    }


@app.get("/api/demand")
def demand_endpoint(service_type: str = "ac repair"):
    """Returns dynamic demand forecasting and surge recommendation multipliers."""
    from tools.optimization_tool import get_demand_forecast
    return get_demand_forecast(service_type)