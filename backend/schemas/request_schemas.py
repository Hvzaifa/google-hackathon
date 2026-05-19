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


class SelectSlotRequest(BaseModel):
    selected_slot: str