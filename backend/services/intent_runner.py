import json
import os
import time
from google import genai
from openai import OpenAI
from dotenv import load_dotenv

from agents.intent_agent import INTENT_AGENT_PROMPT
from utils.trace import make_trace

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
def _clean_json(text: str) -> str:
    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "", 1).strip()

    if text.startswith("```"):
        text = text.replace("```", "", 1).strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    return text

def run_intent_agent(message: str) -> dict:
    start = time.time()

    prompt = f"""
{INTENT_AGENT_PROMPT}

User message:
{message}
"""

    response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system",
            "content": INTENT_AGENT_PROMPT
        },
        {
            "role": "user",
            "content": message
        }
    ],
    temperature=0.2
)

    raw = response.choices[0].message.content

    try:
        parsed = json.loads(raw)
    except Exception:
        parsed = {
            "service_type": None,
            "issue_description": None,
            "location": None,
            "datetime_preference": None,
            "urgency": "unknown",
            "budget_sensitivity": "unknown",
            "job_complexity": "unknown",
            "constraints": [],
            "user_preferences": [],
            "language_detected": "unknown",
            "missing_fields": ["parse_error"],
            "confidence": 0.0,
            "clarification_question": "Please repeat the service, location, and preferred time.",
            "raw_model_output": raw,
        }

    trace = make_trace(
        step_name="intent",
        input_data={"message": message},
        output_data=parsed,
        tool_called="gemini-2.0-flash-lite",
        start_time=start,
    )

    return {
        "status": (
            "clarification_needed"
            if parsed.get("confidence", 0) < 0.80
            else "intent_extracted"
        ),
        "intent": parsed,
        "agent_trace": [trace],
    }