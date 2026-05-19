import time
from fastapi import APIRouter

from schemas.request_schemas import FeedbackRequest
from db.supabase_client import supabase
from agents.service_quality_agent import ServiceQualityAgent
from tools.reputation_tool import update_provider_reputation
from utils.trace import make_trace

router = APIRouter(prefix="/api", tags=["feedback"])

quality_agent = ServiceQualityAgent()


@router.post("/feedback")
def submit_feedback(body: FeedbackRequest):
    booking_response = (
        supabase
        .table("bookings")
        .select("*")
        .eq("booking_id", body.booking_id)
        .execute()
    )

    if not booking_response.data:
        return {
            "status": "booking_not_found",
            "message": "No persisted booking found for feedback.",
            "booking_id": body.booking_id,
            "possible_reason": (
                "Booking may have used local fallback mode "
                "or does not exist."
            ),
        }

    booking = booking_response.data[0]

    state = {
        "booking": booking,
        "agent_trace": [],
    }

    quality_start = time.time()

    state = quality_agent.run(
        state=state,
        rating=body.rating,
        feedback_text=body.feedback_text,
    )

    quality_trace = make_trace(
        step_name="quality_feedback",
        input_data={
            "rating": body.rating,
            "feedback_text": body.feedback_text,
        },
        output_data=state["quality_feedback"],
        tool_called="service_quality_agent + feedback_analysis_tool",
        start_time=quality_start,
        trace_type="decision",
    )

    state["agent_trace"].append(quality_trace)

    rep_start = time.time()

    reputation_result = update_provider_reputation(
        state["quality_feedback"]
    )

    state["reputation_update"] = reputation_result

    reputation_trace = make_trace(
        step_name="reputation_update",
        input_data=state["quality_feedback"],
        output_data=reputation_result,
        tool_called="provider_reputation_memory_tool",
        start_time=rep_start,
        trace_type="memory_update",
    )

    state["agent_trace"].append(reputation_trace)

    return {
        "status": "feedback_processed",
        "quality_feedback": state["quality_feedback"],
        "reputation_update": state["reputation_update"],
        "agent_trace": state["agent_trace"],
    }