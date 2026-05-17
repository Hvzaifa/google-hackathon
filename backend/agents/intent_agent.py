"""
Intent Agent — Agent 1 of the ServisAI pipeline.

Parses Roman Urdu, Arabic-script Urdu, and mixed-language service requests
into structured JSON intents using dynamic LLM selection and configurations.
"""

from __future__ import annotations

import os
import time
import json
from typing import Any, Dict
from utils.llm_provider import generate_llm_text
from utils.trace import make_trace

INTENT_AGENT_PROMPT = """
You are the Intent Agent for this platform, an AI Service Orchestrator for Pakistan's informal service economy.

You handle noisy multilingual service requests in:
- Urdu
- Roman Urdu
- English
- mixed/code-switched language

Your job is to extract structured intent for downstream agents.

Extract:
- service_type
- issue_description
- location
- datetime_preference
- urgency
- budget_sensitivity
- job_complexity
- constraints
- user_preferences
- language_detected
- missing_fields
- confidence
- clarification_question

Allowed values:
urgency: "urgent", "same_day", "scheduled", "flexible", "unknown"
budget_sensitivity: "high", "medium", "low", "unknown"
job_complexity: "basic", "intermediate", "complex", "unknown"
language_detected: "urdu", "roman_urdu", "english", "mixed", "unknown"

Language detection rules:
- If the text uses Urdu words written in English letters, classify as "roman_urdu".
- If the text mixes English service words with Roman Urdu grammar, classify as "mixed".
- Only classify as "urdu" if the text uses Urdu/Arabic script.
- Example: "kal subah G-13 mein technician chahiye" = "roman_urdu" or "mixed", not "urdu".

Rules:
- Return ONLY valid JSON.
- Do not use markdown.
- Do not add explanations outside JSON.
- Normalize service_type to English, e.g. "AC repair", "plumber", "electrician".
- If service_type, location, or datetime_preference is missing, include it in missing_fields.
- If confidence is below 0.80, ask one clarification_question in the user's language.
- If confidence is 0.80 or higher, clarification_question must be null.
- "bilkul kaam nahi kar raha" means urgent or high severity.
- "budget zyada nahi", "cheap", "kam paisay" means budget_sensitivity high.
- Classify job_complexity:
  basic = simple checkup, installation, cleaning, minor service
  intermediate = repair, troubleshooting, gas refill, part replacement likely
  complex = total failure, safety risk, repeated issue, emergency breakdown

JSON shape:
{
  "service_type": string or null,
  "issue_description": string or null,
  "location": string or null,
  "datetime_preference": string or null,
  "urgency": "urgent" | "same_day" | "scheduled" | "flexible" | "unknown",
  "budget_sensitivity": "high" | "medium" | "low" | "unknown",
  "job_complexity": "basic" | "intermediate" | "complex" | "unknown",
  "constraints": [],
  "user_preferences": [],
  "language_detected": "urdu" | "roman_urdu" | "english" | "mixed" | "unknown",
  "missing_fields": [],
  "confidence": number,
  "clarification_question": string or null
}
"""


class IntentAgent:
    """
    Parses natural language requests into structured service transaction intents.
    """

    name: str = "IntentAgent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute intent extraction.
        Input state expects:
          state["user_message"] : raw multilingual message string
        """
        start = time.time()
        message = state.get("user_message", "")
        use_gemini_state = state.get("use_gemini", False)
        use_gemini_env = os.getenv("USE_GEMINI", "false").lower() == "true"
        should_use_gemini = use_gemini_state or use_gemini_env

        # Dynamic LLM provider selection
        preferred_prov = "gemini" if should_use_gemini else os.getenv("LLM_PROVIDER", "groq").lower()

        raw, tool_called = generate_llm_text(
            prompt=message,
            system_instruction=INTENT_AGENT_PROMPT,
            temperature=0.2,
            max_tokens=600,
            preferred_provider=preferred_prov
        )

        if not raw or tool_called == "none":
            raw = json.dumps({
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
                "missing_fields": ["api_error"],
                "confidence": 0.0,
                "clarification_question": "We are experiencing service difficulties. Please repeat your location and service.",
            })
            tool_called = "intent_error_fallback"

        cleaned = self._clean_json(raw)
        try:
            parsed = json.loads(cleaned)
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

        errs = []
        if parsed.get("missing_fields") and "api_error" in parsed.get("missing_fields"):
            errs.append("LLM generation returned empty response or failed.")
        if parsed.get("missing_fields") and "parse_error" in parsed.get("missing_fields"):
            errs.append("Failed to parse JSON response from LLM.")

        trace = make_trace(
            step_name="intent",
            agent_name=self.name,
            input_data={"message": message},
            output_data=parsed,
            tool_called=tool_called,
            start_time=start,
            status="error" if errs else ("clarification_needed" if parsed.get("confidence", 0) < 0.80 else "success"),
            reasoning_summary=f"Parsed user request language preference '{parsed.get('language_detected')}' with confidence {parsed.get('confidence', 0.0)}.",
            errors=errs if errs else None
        )

        state["intent"] = parsed
        state["intent_status"] = (
            "clarification_needed"
            if parsed.get("confidence", 0) < 0.80
            else "intent_extracted"
        )

        if "agent_trace" not in state:
            state["agent_trace"] = []
        state["agent_trace"].append(trace)

        return state

    def _clean_json(self, text: str) -> str:
        text = text.strip()
        
        # 1. Strip think blocks
        if "<think>" in text and "</think>" in text:
            parts = text.split("</think>", 1)
            if len(parts) > 1:
                text = parts[1].strip()
        elif "<think>" in text:
            if "</think>" in text:
                text = text.split("</think>", 1)[1].strip()
            else:
                first_brace = text.find("{")
                if first_brace != -1:
                    text = text[first_brace:].strip()

        # 2. Strip markdown blocks
        if text.startswith("```json"):
            text = text.replace("```json", "", 1).strip()
        if text.startswith("```"):
            text = text.replace("```", "", 1).strip()
        if text.endswith("```"):
            text = text[:-3].strip()
            
        # 3. Locate the first { and last } to extract JSON block precisely
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            text = text[first_brace:last_brace+1]
            
        return text