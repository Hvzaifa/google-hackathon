"""
Pricing Agent — Agent 4 of the ServisAI pipeline.

Takes matched provider details and intent data to compute a comprehensive
price breakdown. Calls deterministic pricing_tool.py, then uses LLM to generate
customer-facing, polite, multilingual explanations (Urdu, Roman Urdu, English).
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict
from openai import OpenAI
from google import genai

from schemas.pricing_schema import PricingInput, PricingOutput, PriceBreakdown
from tools.pricing_tool import calculate_service_price
from utils.trace import make_trace


class PricingAgent:
    """
    Computes pricing breakouts and crafts user-friendly multilingual explanations.
    """

    name: str = "PricingAgent"

    def __init__(self):
        # Clients are lazily loaded from utils.llm_provider to prevent early initialization warnings
        pass

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute pricing analysis step.
        Expects:
          state["providers"] (list of candidates) OR state["matching"]["ranked_providers"][0] (top provider)
          state["intent"] (parsed intent dict)
        """
        start_time = time.time()

        # ── 1. Gather raw candidate and intent ────────────────────────────
        intent_dict = state.get("intent", {})
        
        # We price the top matched provider candidate from the matching phase
        matching_output = state.get("matching", {})
        ranked_providers = matching_output.get("ranked_providers", [])
        
        if ranked_providers:
            # We have ranked providers from matching agent output
            top_scored = ranked_providers[0]
            # Convert ScoredProvider/dict structure to ProviderCandidate structure
            provider_dict = top_scored.get("provider_data", top_scored)
        elif state.get("providers"):
            # Fallback to first discovery provider
            provider_dict = state["providers"][0]
        else:
            return self._error_state(
                state,
                start_time,
                {},
                "No provider available to price."
            )

        # ── 2. Validate using Pydantic ────────────────────────────────────
        try:
            pricing_input = PricingInput(
                provider=provider_dict,
                intent=intent_dict
            )
        except Exception as exc:
            return self._error_state(
                state,
                start_time,
                {"provider": provider_dict, "intent": intent_dict},
                f"Pydantic input validation failed: {exc}"
            )

        provider = pricing_input.provider
        intent = pricing_input.intent

        # ── 3. Call deterministic calculation tool ────────────────────────
        try:
            breakdown = calculate_service_price(provider, intent)
        except Exception as exc:
            return self._error_state(
                state,
                start_time,
                pricing_input.model_dump(),
                f"Pricing calculation failed: {exc}"
            )

        # ── 4. Construct pricing ranges ───────────────────────────────────
        price_range_min = round(breakdown.total_price * 0.90, 2)
        price_range_max = round(breakdown.total_price * 1.10, 2)

        # ── 5. Generate multilingual customer explanation via LLM ─────────
        language = (intent_dict.get("language_detected") or "english").lower()
        use_gemini_env = os.getenv("USE_GEMINI", "false").lower() == "true"
        use_gemini = state.get("use_gemini", use_gemini_env)
        explanation = self._generate_explanation_with_fallback(
            provider.name, breakdown, language, intent_dict.get("service_type") or "service", use_gemini=use_gemini
        )

        # ── 6. Assemble Output ────────────────────────────────────────────
        pricing_output = PricingOutput(
            provider_name=provider.name,
            price_breakdown=breakdown,
            price_range_min=price_range_min,
            price_range_max=price_range_max,
            explanation=explanation,
            confidence=0.95
        )

        output_dict = pricing_output.model_dump()
        reasoning_summary = (
            f"Calculated quote of PKR {breakdown.total_price} for {provider.name}. "
            f"Base: {breakdown.base_fare}, Distance: {breakdown.distance_fare}, "
            f"Urgency: {breakdown.urgency_surcharge}, Complexity: {breakdown.complexity_surcharge}, "
            f"Materials: {breakdown.materials_cost}. Range: PKR {price_range_min} - {price_range_max}."
        )

        # ── 7. Generate Trace ─────────────────────────────────────────────
        trace = make_trace(
            step_name="pricing",
            agent_name=self.name,
            input_data=pricing_input.model_dump(),
            output_data=dict(output_dict),
            tool_called="calculate_service_price_with_llm_explanation",
            start_time=start_time,
            status="success",
            reasoning_summary=reasoning_summary
        )

        state["pricing"] = output_dict
        state["pricing"]["trace"] = trace

        if "agent_trace" in state:
            state["agent_trace"].append(trace)

        return state

    # ── Helpers ────────────────────────────────────────────────────────────

    def _generate_explanation_with_fallback(
        self,
        provider_name: str,
        breakdown: PriceBreakdown,
        language: str,
        service_type: str,
        use_gemini: bool = False
    ) -> str:
        """
        Generate user-friendly, clean explanation using LLM, with deterministic fallback.
        """
        prompt = f"""
You are the Pricing justification engine for ServisAI, an AI Service Orchestrator for Pakistan's informal economy.
Explain the following price breakdown for {service_type} to the customer in a very polite, transparent, and respectful tone.

Breakdown details (Currency is PKR):
- Provider Name: {provider_name}
- Base Visit Fee: {breakdown.base_fare}
- Distance Travel Fee: {breakdown.distance_fare}
- Urgency Surcharge: {breakdown.urgency_surcharge}
- Job Complexity Surcharge: {breakdown.complexity_surcharge}
- Estimated Parts/Materials Cost: {breakdown.materials_cost}
- Total Price Quote: {breakdown.total_price}

Detected Customer Language Preference: {language}

Instructions:
1. Write the explanation strictly in the requested customer language:
   - If 'urdu': Write in Urdu script (Arabic letters).
   - If 'roman_urdu' or 'mixed': Write in Roman Urdu (Urdu written in English letters, e.g., "Aapka base rate Rs 500 hai...").
   - If 'english' or 'unknown': Write in polite, transparent English.
2. Be transparent. Justify the urgency surcharge if it is greater than 0 (e.g. "urgent checkup requested").
3. Justify the complexity surcharge if greater than 0 (e.g. intermediate/complex repair needed).
4. Do not include markdown codeblocks or JSON tags. Return only the polite explanation string.
"""
        system_instruction = "You are a polite, helpful customer service agent for ServisAI Pakistan."

        preferred_prov = "gemini" if use_gemini else os.getenv("LLM_PROVIDER", "groq").lower()

        from utils.llm_provider import generate_llm_text
        res, actual_provider = generate_llm_text(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.3,
            max_tokens=800,
            preferred_provider=preferred_prov
        )

        if res and actual_provider != "none":
            cleaned_res = res.strip()
            if "<think>" in cleaned_res and "</think>" in cleaned_res:
                parts = cleaned_res.split("</think>", 1)
                if len(parts) > 1:
                    cleaned_res = parts[1].strip()
            elif "<think>" in cleaned_res:
                # If the think block is open, it was truncated inside the think block
                cleaned_res = ""
                
            if cleaned_res:
                return cleaned_res

        # Deterministic High-Quality Fallbacks
        if language in ("roman_urdu", "mixed"):
            urgency_text = ""
            if breakdown.urgency_surcharge > 0:
                urgency_text = f" Jaldi (urgency) service ki wajah se Rs {breakdown.urgency_surcharge} surcharge shamil hai."
            complexity_text = ""
            if breakdown.complexity_surcharge > 0:
                complexity_text = f" Kaam intermediate/complex hone ki wajah se Rs {breakdown.complexity_surcharge} complexity charge lagaya gaya hai."
            materials_text = ""
            if breakdown.materials_cost > 0:
                materials_text = f" Aur spare parts ke liye Rs {breakdown.materials_cost} shamil hain."

            return (
                f"Aapki {service_type} ki kul pricing Rs {breakdown.total_price} calculate hui hai. "
                f"Isme visit base rate Rs {breakdown.base_fare} hai aur distance travel charges Rs {breakdown.distance_fare} hain.{urgency_text}{complexity_text}{materials_text} "
                f"Hamare partner {provider_name} aapke diye gaye location par jald pohnchenge. Shukriya!"
            )
            
        elif language == "urdu":
            urgency_text = ""
            if breakdown.urgency_surcharge > 0:
                urgency_text = f" جلدی سروس کی وجہ سے Rs {breakdown.urgency_surcharge} سرچارج شامل ہے۔"
            complexity_text = ""
            if breakdown.complexity_surcharge > 0:
                complexity_text = f" کام کی نوعیت پیچیدہ ہونے کی وجہ سے Rs {breakdown.complexity_surcharge} اضافی چارج شامل کیا گیا ہے۔"
            materials_text = ""
            if breakdown.materials_cost > 0:
                materials_text = f" اور متوقع سامان کے اخراجات Rs {breakdown.materials_cost} ہیں۔"

            return (
                f"آپ کی {service_type} سروس کی کل قیمت Rs {breakdown.total_price} مقرر کی گئی ہے۔ "
                f"جس میں وزٹ فیس Rs {breakdown.base_fare} اور فاصلے کے اخراجات Rs {breakdown.distance_fare} ہیں۔{urgency_text}{complexity_text}{materials_text} "
                f"ہمارے پارٹنر {provider_name} آپ کی لوکیشن پر سروس کے لیے تیار ہیں۔ شکریہ!"
            )
            
        else: # English / default
            urgency_text = ""
            if breakdown.urgency_surcharge > 0:
                urgency_text = f" An urgency surcharge of PKR {breakdown.urgency_surcharge} is added due to same-day request."
            complexity_text = ""
            if breakdown.complexity_surcharge > 0:
                complexity_text = f" A complexity fee of PKR {breakdown.complexity_surcharge} is applied as diagnostic needs tools."
            materials_text = ""
            if breakdown.materials_cost > 0:
                materials_text = f" Estimated parts/materials cost is PKR {breakdown.materials_cost}."

            return (
                f"The total estimated cost for your {service_type} is PKR {breakdown.total_price}. "
                f"This consists of a base inspection fee of PKR {breakdown.base_fare} and travel fare of PKR {breakdown.distance_fare}.{urgency_text}{complexity_text}{materials_text} "
                f"Our verified partner {provider_name} is ready to serve you. Thank you for choosing ServisAI!"
            )

    def _error_state(
        self,
        state: Dict[str, Any],
        start_time: float,
        input_snapshot: Any,
        error_msg: str,
    ) -> Dict[str, Any]:
        """Record error state in pricing block."""
        trace = make_trace(
            step_name="pricing",
            agent_name=self.name,
            input_data=input_snapshot,
            output_data={},
            tool_called="pricing_error_fallback",
            start_time=start_time,
            status="error",
            reasoning_summary=f"Pricing agent error: {error_msg}",
            errors=[error_msg]
        )
        state["pricing"] = {
            "status": "error",
            "error": error_msg,
            "trace": trace
        }
        if "agent_trace" in state:
            state["agent_trace"].append(trace)
        return state
