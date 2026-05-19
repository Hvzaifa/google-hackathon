from fastapi import APIRouter

from schemas.request_schemas import IntentRequest
from orchestration.service_pipeline import service_pipeline
from utils.response_formatter import format_orchestration_response

router = APIRouter(prefix="/api", tags=["orchestration"])


@router.post("/orchestrate")
def orchestrate(body: IntentRequest):
    initial_state = {
        "user_message": body.message,
        "user_id": body.user_id,
        "agent_trace": [],
        "simulation_flags": {
            "simulate_maps_failure": body.simulate_maps_failure,
            "simulate_no_providers": body.simulate_no_providers,
            "simulate_booking_failure": body.simulate_booking_failure,
            "simulate_payment_failure": body.simulate_payment_failure,
            "simulate_provider_cancellation": body.simulate_provider_cancellation,
        },
    }

    final_state = service_pipeline.run(initial_state)

    return format_orchestration_response(final_state)