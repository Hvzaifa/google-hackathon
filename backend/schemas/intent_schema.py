"""
Pydantic schema for Intent Agent output validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class IntentSchema(BaseModel):
    service_type: Optional[str] = None
    issue_description: Optional[str] = None
    location: Optional[str] = None
    datetime_preference: Optional[str] = None
    urgency: str = Field(..., pattern=r"^(urgent|same_day|scheduled|flexible|unknown)$")
    budget_sensitivity: str = Field(..., pattern=r"^(high|medium|low|unknown)$")
    job_complexity: str = Field(..., pattern=r"^(basic|intermediate|complex|unknown)$")
    constraints: List[str] = []
    user_preferences: List[str] = []
    language_detected: str = Field(..., pattern=r"^(urdu|roman_urdu|english|mixed|unknown)$")
    missing_fields: List[str] = []
    confidence: float = Field(..., ge=0.0, le=1.0)
    clarification_question: Optional[str] = None