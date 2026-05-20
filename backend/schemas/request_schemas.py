from pydantic import BaseModel


class IntentRequest(BaseModel):
    message: str
    user_id: str = "anonymous"

    simulate_maps_failure: bool = False
    simulate_no_providers: bool = False
    simulate_booking_failure: bool = False
    simulate_payment_failure: bool = False
    simulate_provider_cancellation: bool = False


class FeedbackRequest(BaseModel):
    booking_id: str
    rating: int
    feedback_text: str


class BookRequest(BaseModel):
    user_id: str = "anonymous"
    intent: dict
    selected_provider: dict
    pricing: dict
    agent_trace: list = []
    simulation_flags: dict = {}


class SelectSlotRequest(BaseModel):
    selected_slot: str