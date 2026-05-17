"""
Pydantic schemas for Matching Agent input/output validation.

Defines the contract between Discovery → Matching and Matching → Pricing.
All scoring factors are captured in ScoreBreakdown for full transparency.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------

class ProviderCandidate(BaseModel):
    """A single provider candidate coming from Discovery Agent output."""
    name: str
    rating: float = Field(default=3.5, ge=0.0, le=5.0)
    review_count: int = Field(default=0, ge=0)
    distance_km: float = Field(default=5.0, ge=0.0)
    available: bool = Field(default=True, alias="available")
    base_rate: int = Field(default=500, ge=0)
    per_km_rate: int = Field(default=25, ge=0)
    on_time_score: float = Field(default=0.80, ge=0.0, le=1.0)
    cancellation_rate: float = Field(default=0.10, ge=0.0, le=1.0)
    risk_score: float = Field(default=0.20, ge=0.0, le=1.0,
        description="Composite risk score: 0 = low risk (good), 1 = high risk (bad). "
                    "Derived from complaint history, repeated cancellations, blacklist flags.")
    review_recency: float = Field(default=0.75, ge=0.0, le=1.0)
    complexity_level: str = Field(
        default="intermediate",
        pattern=r"^(basic|intermediate|complex)$",
    )
    # Pass-through fields (not used for scoring, but preserved in output)
    service_type: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    place_id: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    sector: Optional[str] = None
    city: Optional[str] = None
    specialization: Optional[str] = None

    model_config = {"populate_by_name": True}


class IntentData(BaseModel):
    """Subset of intent fields relevant to matching decisions."""
    service_type: Optional[str] = None
    urgency: str = Field(default="unknown", pattern=r"^(urgent|same_day|scheduled|flexible|unknown)$")
    budget_sensitivity: str = Field(default="unknown", pattern=r"^(high|medium|low|unknown)$")
    job_complexity: str = Field(default="unknown", pattern=r"^(basic|intermediate|complex|unknown)$")
    user_preferences: List[str] = []
    constraints: List[str] = []


class MatchingInput(BaseModel):
    """Full input to the Matching Agent."""
    providers: List[ProviderCandidate] = []
    intent: IntentData = Field(default_factory=IntentData)


# ---------------------------------------------------------------------------
# Output schemas
# ---------------------------------------------------------------------------

class ScoreBreakdown(BaseModel):
    distance: float = Field(..., ge=0.0, le=1.0)
    rating: float = Field(..., ge=0.0, le=1.0)
    review_recency: float = Field(..., ge=0.0, le=1.0)
    on_time_score: float = Field(..., ge=0.0, le=1.0)       # NEW — split from reliability
    cancellation_risk: float = Field(..., ge=0.0, le=1.0)   # NEW — split from reliability
    risk_score: float = Field(..., ge=0.0, le=1.0)          # NEW — composite provider risk
    price_fit: float = Field(..., ge=0.0, le=1.0)
    specialization: float = Field(..., ge=0.0, le=1.0)
    user_preference: float = Field(..., ge=0.0, le=1.0)     # NEW — preference match score
    availability: float = Field(..., ge=0.0, le=1.0)


class ScoredProvider(BaseModel):
    """A provider with its computed match score and breakdown."""
    name: str
    overall_score: float = Field(..., ge=0.0, le=1.0)
    score_breakdown: ScoreBreakdown
    rank: int = Field(..., ge=1)
    reasoning: str
    # Original provider data preserved for downstream agents
    provider_data: dict = {}


class MatchingOutput(BaseModel):
    """Full output from the Matching Agent."""
    status: str = Field(..., pattern=r"^(success|fallback|error)$")
    ranked_providers: List[ScoredProvider] = []
    total_candidates: int = Field(..., ge=0)
    available_candidates: int = Field(..., ge=0)
    reasoning_summary: str

    @field_validator("ranked_providers")
    @classmethod
    def limit_ranked(cls, v: List[ScoredProvider]) -> List[ScoredProvider]:
        """Ensure we return at most 5 ranked providers."""
        return v[:5]
