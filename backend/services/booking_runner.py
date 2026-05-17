"""
Booking agent runner service wrapping the BookingAgent execution.
"""

from dotenv import load_dotenv
from agents.booking_agent import BookingAgent

load_dotenv()
booking_agent = BookingAgent()


def run_booking_agent(state: dict) -> dict:
    """
    Executes the standalone booking agent with loaded environment configuration.
    """
    return booking_agent.run(state)
