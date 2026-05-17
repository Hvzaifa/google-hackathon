"""
Pydantic schemas for the Booking Agent.
Defines inputs and outputs for booking confirmation and collision simulation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from schemas.matching_schema import IntentData


class BookingInput(BaseModel):
    """Input payload for confirming or simulating a service provider booking."""
    provider_name: str = Field(..., description="Name of the selected provider")
    appointment_time: str = Field(..., description="Requested date and time of appointment (e.g. YYYY-MM-DD HH:MM)")
    total_price: float = Field(..., description="The agreed total price from the Pricing Agent")
    user_confirmed: bool = Field(default=True, description="Whether the user confirmed the price quote")
    intent: IntentData = Field(..., description="Service intent for tracking and context")


class BookingOutput(BaseModel):
    """Output containing booking receipt, scheduling status, or collision options."""
    booking_id: Optional[str] = Field(default=None, description="Unique booking ID generated on successful confirmation")
    status: str = Field(..., pattern=r"^(confirmed|conflict|cancelled)$", description="The outcome of the scheduling attempt")
    provider_name: str = Field(..., description="Name of the provider booked or requested")
    appointment_time: str = Field(..., description="Final or requested appointment time")
    total_price: float = Field(..., description="The total booking fare")
    alternative_slots: List[str] = Field(default_factory=list, description="Suggestions for alternative times in case of schedule collision")
    alternative_providers: List[str] = Field(default_factory=list, description="Suggestions for alternative matched providers in case of schedule collision")
    reminders_sent: List[str] = Field(default_factory=list, description="Log of pre-service notification reminders dispatched")
    progress_updates: List[str] = Field(default_factory=list, description="Simulated progress journey logs showing service lifecycle events")
    message: str = Field(..., description="Friendly, clear, multilingual notification detailing confirmation status or conflict options")
    waitlist_id: Optional[str] = Field(default=None, description="Waitlist ID if user was queued on conflict")
    waitlist_position: Optional[int] = Field(default=None, description="1-based queue position on the waitlist")
    auto_rescheduled: bool = Field(default=False, description="True if booking was auto-confirmed via waitlist promotion")
