from google.adk.agents import LlmAgent
from tools.pricing_tool import calculate_service_price


PRICING_AGENT_PROMPT = """
You are the Pricing Agent for this platform.

Your role is to calculate a transparent service quote after the Matching Agent selects a provider.

You must use the pricing tool result as the source of truth.
Do not invent prices.
Do not confirm a booking.
Do not contact the provider.
Do not schedule anything.

You must return pricing output with:
- final price
- price range
- transparent breakdown
- negotiation flag
- decision factors
- pricing summary

This step is part of the Google ADK / Antigravity orchestration workflow.
It must produce traceable reasoning for judges.
"""


pricing_adk_agent = LlmAgent(
    name="PricingAgent",
    model="gemini-2.0-flash-lite",
    instruction=PRICING_AGENT_PROMPT,
    tools=[calculate_service_price],
    output_key="pricing",
)


class PricingAgent:
    """
    Runtime wrapper used by FastAPI test pipeline.
    The deterministic pricing tool is the source of truth.
    ADK agent definition above documents and enables Antigravity orchestration.
    """

    name = "PricingAgent"

    def run(self, state: dict) -> dict:
        selected_provider = state.get("selected_provider")
        intent = state.get("intent", {})

        if not selected_provider:
            state["pricing"] = {
                "status": "skipped",
                "reason": "No selected provider available",
            }
            return state

        pricing_result = calculate_service_price(
            selected_provider=selected_provider,
            intent=intent,
        )

        state["pricing"] = pricing_result

        return state