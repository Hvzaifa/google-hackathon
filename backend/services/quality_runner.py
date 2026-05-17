"""
Quality agent runner service wrapping the QualityAgent execution.
"""

from dotenv import load_dotenv
from agents.quality_agent import QualityAgent

load_dotenv()
quality_agent = QualityAgent()


def run_quality_agent(state: dict) -> dict:
    """
    Executes the standalone quality/dispute agent with loaded environment configuration.
    """
    return quality_agent.run(state)
