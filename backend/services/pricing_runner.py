"""
Pricing agent runner service wrapping the PricingAgent execution.
"""

from dotenv import load_dotenv
from agents.pricing_agent import PricingAgent

load_dotenv()
pricing_agent = PricingAgent()


def run_pricing_agent(state: dict) -> dict:
    """
    Executes the standalone pricing agent with loaded environment configuration.
    """
    return pricing_agent.run(state)
