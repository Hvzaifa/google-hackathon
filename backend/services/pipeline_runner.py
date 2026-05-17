"""
Pipeline runner service wrapping the PipelineOrchestrator execution.
"""

from dotenv import load_dotenv
from agents.pipeline import PipelineOrchestrator

load_dotenv()
pipeline_orchestrator = PipelineOrchestrator()


def run_full_pipeline(
    message: str,
    appointment_time: str = "2026-05-18 15:00",
    rating: int = 5,
    review_text: str = "Excellent service! Kamran was highly professional and on-time.",
    issue_reported: bool = False,
    use_gemini: bool = False
) -> dict:
    """
    Runs a full pipeline execution simulation wrapping PipelineOrchestrator.
    """
    return pipeline_orchestrator.run_full_simulation(
        message=message,
        appointment_time=appointment_time,
        rating=rating,
        review_text=review_text,
        issue_reported=issue_reported,
        use_gemini=use_gemini
    )


def run_pipeline_step(state: dict) -> dict:
    """
    Runs a state-by-state pipeline step transition.
    """
    return pipeline_orchestrator.run_pipeline(state)
