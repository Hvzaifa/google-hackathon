"""
Quality Agent — Agent 6 of the ServisAI pipeline.

Handles post-service rating collection, updates provider reputation scores in state,
detects negative review sentiment, and automates dispute resolution and escalation paths.
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict
from openai import OpenAI
from google import genai

from schemas.quality_schema import QualityInput, QualityOutput
from tools.reputation_tool import calculate_new_reputation, process_dispute_resolution
from utils.trace import make_trace


class QualityAgent:
    """
    Orchestrates review parsing, Bayesian reputation updates, and multilingual dispute resolution.
    """

    name: str = "QualityAgent"

    def __init__(self):
        # Clients are lazily loaded from utils.llm_provider to prevent early initialization warnings
        pass

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute quality feedback and dispute handling step.
        Expects:
          state["quality_request"] (feedback input payload)
          state["booking"] (to extract defaults if request fields are empty)
        """
        start_time = time.time()

        # ── 1. Gather raw parameters ──────────────────────────────────────
        quality_request = state.get("quality_request", {})
        booking_data = state.get("booking", {})

        booking_id = quality_request.get("booking_id") or booking_data.get("booking_id")
        provider_name = quality_request.get("provider_name") or booking_data.get("provider_name")
        rating = quality_request.get("rating")
        review_text = quality_request.get("review_text", "")
        issue_reported = quality_request.get("issue_reported", False)
        photo_evidence_urls = quality_request.get("photo_evidence_urls", [])
        completion_checklist = quality_request.get("completion_checklist", {})
        dispute_type = quality_request.get("dispute_type", "general")

        # Auto-flag issue if completion checklist has a failure
        if not issue_reported and completion_checklist:
            if any(val is False for val in completion_checklist.values()):
                issue_reported = True

        evidence_received = len(photo_evidence_urls) > 0
        checklist_passed = None
        if completion_checklist:
            checklist_passed = all(val is True for val in completion_checklist.values())

        if not booking_id or not provider_name:
            return self._error_state(
                state,
                start_time,
                {},
                "Missing booking_id or provider_name. Provide booking reference details."
            )

        if rating is None:
            # Default rating to 5 if not provided (happy customer scenario)
            rating = 5

        # ── 2. Validate using Pydantic ────────────────────────────────────
        try:
            quality_input = QualityInput(
                booking_id=booking_id,
                provider_name=provider_name,
                rating=rating,
                review_text=review_text,
                issue_reported=issue_reported,
                photo_evidence_urls=photo_evidence_urls,
                completion_checklist=completion_checklist,
                dispute_type=dispute_type
            )
        except Exception as exc:
            return self._error_state(
                state,
                start_time,
                {
                    "booking_id": booking_id,
                    "provider_name": provider_name,
                    "rating": rating,
                    "review_text": review_text,
                    "issue_reported": issue_reported,
                    "photo_evidence_urls": photo_evidence_urls,
                    "completion_checklist": completion_checklist,
                    "dispute_type": dispute_type
                },
                f"Pydantic input validation failed: {exc}"
            )

        # ── 3. Find current provider metrics from state to update score ───
        current_rating = 4.2
        current_review_count = 20

        # Try to locate provider in active state pool
        provider_state_ref = None
        providers_list = state.get("providers", [])
        for p in providers_list:
            if p.get("name") == provider_name:
                current_rating = p.get("rating", current_rating)
                current_review_count = p.get("review_count", current_review_count)
                provider_state_ref = p
                break

        # ── 4. Call deterministic reputation & dispute tools ──────────────
        try:
            new_rating, new_count = calculate_new_reputation(
                current_rating=current_rating,
                current_review_count=current_review_count,
                new_user_rating=rating
            )
            
            # Mutate state inline to keep reputation persistent across cycles
            if provider_state_ref is not None:
                provider_state_ref["rating"] = new_rating
                provider_state_ref["review_count"] = new_count
                
        except Exception as exc:
            return self._error_state(
                state,
                start_time,
                quality_input.model_dump(),
                f"Reputation update calculations failed: {exc}"
            )

        try:
            status, actions_taken, escalation_reason = process_dispute_resolution(
                rating=rating,
                review_text=review_text,
                issue_reported=issue_reported,
                dispute_type=dispute_type
            )
        except Exception as exc:
            return self._error_state(
                state,
                start_time,
                quality_input.model_dump(),
                f"Dispute resolution process failed: {exc}"
            )

        # ── 5. Run sentiment and multilingual reply generation via LLM ────
        intent_dict = state.get("intent", {})
        language = (intent_dict.get("language_detected") or "english").lower()
        use_gemini_env = os.getenv("USE_GEMINI", "false").lower() == "true"
        use_gemini = state.get("use_gemini", use_gemini_env)

        sentiment, resolution_message = self._analyze_feedback_with_llm(
            rating=rating,
            review_text=review_text,
            status=status,
            language=language,
            provider_name=provider_name,
            use_gemini=use_gemini
        )

        # ── 6. Assemble Output ────────────────────────────────────────────
        quality_output = QualityOutput(
            booking_id=booking_id,
            provider_name=provider_name,
            status=status,
            rating_given=rating,
            review_sentiment=sentiment,
            actions_taken=actions_taken,
            escalation_required=(status == "dispute_escalated"),
            escalation_reason=escalation_reason if status == "dispute_escalated" else None,
            new_provider_rating=new_rating,
            new_provider_review_count=new_count,
            resolution_message=resolution_message,
            evidence_received=evidence_received,
            checklist_passed=checklist_passed
        )

        output_dict = quality_output.model_dump()
        reasoning_summary = (
            f"Review processed for {provider_name} [Booking: {booking_id}]. "
            f"Rating: {rating} -> New reputation: {new_rating} ({new_count} reviews). "
            f"Dispute status: {status}. Actions: {', '.join(actions_taken)}."
        )

        # ── 7. Generate Trace ─────────────────────────────────────────────
        trace = make_trace(
            step_name="quality",
            agent_name=self.name,
            input_data=quality_input.model_dump(),
            output_data=dict(output_dict),
            tool_called="update_reputation_and_resolve_disputes",
            start_time=start_time,
            status="error" if status == "dispute_escalated" else ("fallback" if status == "dispute_resolved" else "success"),
            reasoning_summary=reasoning_summary
        )

        state["quality"] = output_dict
        state["quality"]["trace"] = trace

        if "agent_trace" in state:
            state["agent_trace"].append(trace)

        return state

    # ── Helpers ────────────────────────────────────────────────────────────

    def _analyze_feedback_with_llm(
        self,
        rating: int,
        review_text: str,
        status: str,
        language: str,
        provider_name: str,
        use_gemini: bool = False
    ) -> tuple[str, str]:
        """
        Analyze feedback text to detect sentiment and craft a supportive customer-care message.
        """
        # Determine sentiment deterministically as initial fallback
        sentiment = "neutral"
        if rating >= 4:
            sentiment = "positive"
        elif rating <= 2:
            sentiment = "negative"

        prompt = f"""
You are the Quality and Customer-Care engine for ServisAI Pakistan.
Analyze this user review and compose:
1. Sentiment: positive, neutral, or negative.
2. Support Response: A highly professional, polite customer care response in the user's language.

Review Details:
- Rating Given: {rating} stars
- Provider Name: {provider_name}
- Review Text: "{review_text}"
- Dispute Status: {status}
- Preferred Language: {language}

Instructions:
1. Reply strictly in the user's preferred language:
   - If 'urdu': Write in Urdu script (Arabic letters).
   - If 'roman_urdu' or 'mixed': Write in Roman Urdu (Urdu written in English letters).
   - If 'english' or 'unknown': Write in polite, transparent English.
2. If status is 'dispute_escalated': Apologize profusely, guarantee that senior operations management is auditing the provider's behavior, and state that their safety/satisfaction is our absolute priority.
3. If status is 'dispute_resolved': Apologize for the inconvenience, confirm that we have issued PKR 300 compensation credit to their wallet, and sent a formal warning to the partner.
4. If status is 'reputation_updated': Thank them warmly for their review and wish them a wonderful day.
5. Format your output EXACTLY as:
   SENTIMENT: [sentiment]
   RESPONSE: [support response text]
"""
        system_instruction = "You are a polite, helpful customer loyalty manager for ServisAI Pakistan."

        preferred_prov = "gemini" if use_gemini else os.getenv("LLM_PROVIDER", "groq").lower()

        from utils.llm_provider import generate_llm_text
        res, actual_provider = generate_llm_text(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.2,
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
                # Truncated inside think block
                cleaned_res = ""

            if cleaned_res and "SENTIMENT:" in cleaned_res and "RESPONSE:" in cleaned_res:
                parts = cleaned_res.split("RESPONSE:")
                sent_part = parts[0].replace("SENTIMENT:", "").strip().lower()
                resp_part = parts[1].strip()
                
                if "positive" in sent_part:
                    sentiment = "positive"
                elif "negative" in sent_part:
                    sentiment = "negative"
                else:
                    sentiment = "neutral"
                    
                return sentiment, resp_part

        # Deterministic Support Response Fallbacks
        if status == "dispute_escalated":
            if language in ("roman_urdu", "mixed"):
                resp = (
                    f"Hamein is kharab tajurbe par nihayat afsos hai. Humne aapke dispute ko "
                    f"priority desk par escalate kar diya hai aur {provider_name} ka account "
                    f"auditing ke liye suspend kar diya hai. Hamari safety team jald aap se rabta karegi."
                )
            elif language == "urdu":
                resp = (
                    f"ہمیں اس برے تجربے پر نہایت افسوس ہے۔ ہم نے آپ کی شکایت کو "
                    f"ترجیحی ڈیسک پر منتقل کر دیا ہے اور {provider_name} کا اکاؤنٹ "
                    f"عارضی طور پر معطل کر دیا ہے۔ ہماری سیفٹی ٹیم جلد ہی آپ سے رابطہ کرے گی۔"
                )
            else:
                resp = (
                    f"We are deeply sorry for this highly unacceptable experience. We have escalated your "
                    f"dispute to our priority safety desk and temporarily suspended {provider_name}'s account. "
                    f"A senior manager will contact you immediately for verification."
                )
        elif status == "dispute_resolved":
            if language in ("roman_urdu", "mixed"):
                resp = (
                    f"Aapki shikayat ke liye hum sharminda hain. Hamein behtar karne ka mauqa dene ke liye, "
                    f"humne aapke wallet mein PKR 300 compensation credit add kar diya hai aur "
                    f"{provider_name} ko warning bhej di hai. Shukriya!"
                )
            elif language == "urdu":
                resp = (
                    f"آپ کی شکایت کے لیے ہم معذرت خواہ ہیں۔ ہم نے آپ کے والٹ میں "
                    f"Rs 300 کی رقم معاوضے کے طور پر جمع کر دی ہے اور "
                    f"{provider_name} کو تنبیہی نوٹس جاری کر دیا ہے۔ شکریہ!"
                )
            else:
                resp = (
                    f"We apologize sincerely for the inconvenience. To make things right, we have credited "
                    f"PKR 300 compensation credit to your wallet and issued a formal warning to {provider_name}."
                )
        else: # reputation_updated
            if language in ("roman_urdu", "mixed"):
                resp = f"Feedback ka buhat shukriya! {provider_name} ke sath kaam karne par khushi hui."
            elif language == "urdu":
                resp = f"آپ کے فیڈ بیک کا بہت شکریہ! {provider_name} کے ساتھ آپ کا کام مکمل ہونے پر خوشی ہوئی۔"
            else:
                resp = f"Thank you so much for your rating! We are glad {provider_name} served you well today."

        return sentiment, resp

    def _error_state(
        self,
        state: Dict[str, Any],
        start_time: float,
        input_snapshot: Any,
        error_msg: str,
    ) -> Dict[str, Any]:
        """Record error state in quality block."""
        trace = make_trace(
            step_name="quality",
            agent_name=self.name,
            input_data=input_snapshot,
            output_data={},
            tool_called="quality_error_fallback",
            start_time=start_time,
            status="error",
            reasoning_summary=f"Quality agent error: {error_msg}",
            errors=[error_msg]
        )
        state["quality"] = {
            "status": "error",
            "error": error_msg,
            "trace": trace
        }
        if "agent_trace" in state:
            state["agent_trace"].append(trace)
        return state
