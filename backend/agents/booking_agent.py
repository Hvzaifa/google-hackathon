from google.adk.agents import LlmAgent

from tools.booking_tool import create_booking_record


BOOKING_AGENT_PROMPT = """
You are the Booking Agent for this platform..

You finalize service workflow execution after:
- provider selection
- pricing calculation

You must:
- generate booking confirmation
- persist booking lifecycle state
- return booking metadata
- maintain orchestration traceability

You must use deterministic booking tool output as source of truth.

Do not:
- recalculate prices
- rerank providers
- hallucinate provider data

This booking workflow is part of the
Google ADK / Antigravity orchestration pipeline.
"""


booking_adk_agent = LlmAgent(
    name="BookingAgent",
    model="gemini-2.0-flash-lite",
    instruction=BOOKING_AGENT_PROMPT,
    tools=[create_booking_record],
    output_key="booking",
)


class BookingAgent:
    """
    Runtime orchestration wrapper.
    """

    name = "BookingAgent"

    def run(self, state: dict) -> dict:

        selected_provider = state.get(
            "selected_provider"
        )

        pricing = state.get("pricing")

        intent = state.get("intent")

        user_id = state.get("user_id", "anonymous")

        if not selected_provider:
            state["booking"] = {
                "status": "skipped",
                "reason": "No provider selected"
            }
            return state

        booking_result = create_booking_record(
            user_id=user_id,
            intent=intent,
            selected_provider=selected_provider,
            pricing=pricing,
        )

        state["booking"] = booking_result

        return state