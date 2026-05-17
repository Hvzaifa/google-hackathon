"""
Pydantic schemas for the Quality/Dispute Agent.
Defines inputs and outputs for review collection, reputation updates, and dispute handling.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class QualityInput(BaseModel):
    """Input payload representing customer-provided review and feedback or dispute claim."""
    booking_id: str = Field(..., description="The reference booking ID")
    provider_name: str = Field(..., description="Name of the service provider reviewed")
    rating: int = Field(..., ge=1, le=5, description="Provider rating score from 1 to 5")
    review_text: str = Field(..., description="Multilingual text review from the customer")
    issue_reported: bool = Field(default=False, description="Flag indicating if a dispute or safety/quality issue is reported")
    photo_evidence_urls: List[str] = Field(default_factory=list, description="URLs to photos/videos of completed work or dispute issues")
    completion_checklist: Dict[str, bool] = Field(default_factory=dict, description="Task checklist (e.g. 'compressor cleaned': True)")
    dispute_type: str = Field(default="general", description="Specific dispute scenario code: general | no_show | cancellation | price_disagreement | overrun")


class QualityOutput(BaseModel):
    """Output details representing feedback processing, rating updates, or dispute escalations."""
    booking_id: str = Field(..., description="The reference booking ID")
    provider_name: str = Field(..., description="Name of the service provider reviewed")
    status: str = Field(..., pattern=r"^(reputation_updated|dispute_resolved|dispute_escalated)$", description="The feedback processing status")
    rating_given: int = Field(..., ge=1, le=5, description="The customer rating analyzed")
    review_sentiment: str = Field(..., description="Analyzed sentiment of review_text (positive, neutral, negative)")
    actions_taken: List[str] = Field(default_factory=list, description="Remedial actions (coupons, notifications, warnings)")
    escalation_required: bool = Field(default=False, description="True if manual human escalation is required")
    escalation_reason: Optional[str] = Field(default=None, description="Detailed reason for human escalation, if status is dispute_escalated")
    new_provider_rating: float = Field(..., ge=0.0, le=5.0, description="The updated average rating of the provider")
    new_provider_review_count: int = Field(..., ge=0, description="The updated review total for the provider")
    resolution_message: str = Field(..., description="Multilingual resolution or customer-care statement (Urdu, Roman Urdu, or English)")
    evidence_received: bool = Field(default=False, description="Whether uploaded media assets were successfully processed")
    checklist_passed: Optional[bool] = Field(default=None, description="Whether the completion checklist was fully satisfied")
