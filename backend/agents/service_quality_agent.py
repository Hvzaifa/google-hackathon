from google.adk.agents import LlmAgent

from tools.feedback_tool import analyze_feedback


QUALITY_AGENT_PROMPT = """
You are the ServiceQualityAgent for this platform.

You handle:
- feedback analysis
- quality assessment
- dispute classification
- escalation simulation
- provider reputation impact

You must:
- classify complaint severity
- determine escalation need
- simulate compensation decisions
- update future matching impact

This workflow is part of the
Google ADK / Antigravity orchestration system.
"""


quality_adk_agent = LlmAgent(
    name="ServiceQualityAgent",
    model="gemini-2.0-flash-lite",
    instruction=QUALITY_AGENT_PROMPT,
    tools=[analyze_feedback],
    output_key="quality_feedback",
)


class ServiceQualityAgent:

    name = "ServiceQualityAgent"

    def run(
        self,
        state: dict,
        rating: int,
        feedback_text: str,
    ) -> dict:

        booking = state.get("booking")

        feedback_result = analyze_feedback(
            booking=booking,
            rating=rating,
            feedback_text=feedback_text,
        )

        state["quality_feedback"] = feedback_result

        return state


        