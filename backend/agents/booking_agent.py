"""
Booking Agent — Agent 5 of the ServisAI pipeline.

Handles final booking reservation, collision check simulation, scheduling fallback 
generation, and progress tracking journey updates. Uses LLM to explain conflicts or confirmations.
"""

from __future__ import annotations

import os
import random
import time
from typing import Any, Dict, List
from openai import OpenAI
from google import genai

from schemas.booking_schema import BookingInput, BookingOutput
from tools.booking_tool import check_booking_collision, generate_booking_receipt
from tools.waitlist_tool import add_to_waitlist, get_waitlist_position
from utils.trace import make_trace


class BookingAgent:
    """
    Manages booking schedule verification, double-booking fallbacks, and journey progress logs.
    """

    name: str = "BookingAgent"

    def __init__(self):
        # Clients are lazily loaded from utils.llm_provider to prevent early initialization warnings
        pass

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute booking reservation step.
        Expects:
          state["pricing"] (pricing output payload)
          state["intent"] (service intent dict)
          state["booking_request"] (dict containing "appointment_time" and "user_confirmed")
        """
        start_time = time.time()

        # ── 1. Gather raw parameters ──────────────────────────────────────
        pricing_data = state.get("pricing", {})
        intent_dict = state.get("intent", {})
        booking_request = state.get("booking_request", {})

        provider_name = pricing_data.get("provider_name")
        total_price = pricing_data.get("price_breakdown", {}).get("total_price", 0.0)

        # Fallback to sensible time if booking time isn't explicitly set
        appointment_time = booking_request.get("appointment_time")
        if not appointment_time:
            # Set default appointment time (e.g. tomorrow at 3 PM odd hour for success)
            appointment_time = "2026-05-18 15:00"

        user_confirmed = booking_request.get("user_confirmed", True)

        if not provider_name:
            return self._error_state(
                state,
                start_time,
                {},
                "No priced provider found. Run pricing agent first."
            )

        # ── 2. Validate using Pydantic ────────────────────────────────────
        try:
            booking_input = BookingInput(
                provider_name=provider_name,
                appointment_time=appointment_time,
                total_price=total_price,
                user_confirmed=user_confirmed,
                intent=intent_dict
            )
        except Exception as exc:
            return self._error_state(
                state,
                start_time,
                {
                    "provider_name": provider_name,
                    "appointment_time": appointment_time,
                    "total_price": total_price,
                    "user_confirmed": user_confirmed
                },
                f"Pydantic input validation failed: {exc}"
            )

        # ── 3. Check for double booking collision ────────────────────────
        # Extract potential alternative providers from the matched providers state pool
        alternative_providers_pool = []
        matching_output = state.get("matching", {})
        ranked = matching_output.get("ranked_providers", [])
        if ranked:
            alternative_providers_pool = [p.get("name") for p in ranked if p.get("name") != provider_name]
        elif state.get("providers"):
            alternative_providers_pool = [p.get("name") for p in state["providers"] if p.get("name") != provider_name]

        provider_distance = 5.0
        # Try to find the distance of the selected provider
        for p in (ranked or state.get("providers", [])):
            if p.get("name") == provider_name:
                provider_distance = p.get("distance_km", 5.0)
                break

        try:
            status, alt_slots, alt_provs = check_booking_collision(
                provider_name=provider_name,
                appointment_time=appointment_time,
                alternative_providers_pool=alternative_providers_pool,
                distance_km=provider_distance
            )
        except Exception as exc:
            return self._error_state(
                state,
                start_time,
                booking_input.model_dump(),
                f"Collision check failed: {exc}"
            )

        booking_id = None
        reminders_sent = []
        progress_updates = []
        waitlist_id = None
        waitlist_position = None
        auto_rescheduled = booking_request.get("auto_rescheduled", False)

        # ── 4. Process Confirmation or Conflict status ─────────────────────
        if status == "confirmed":
            booking_id = f"BK-{random.randint(10000, 99999)}"
            reminders_sent, progress_updates, default_checklist = generate_booking_receipt(
                booking_id, provider_name, total_price
            )
            state["pending_checklist"] = default_checklist
            from tools.optimization_tool import record_booking
            record_booking(provider_name=provider_name, total_price=total_price)
        elif status == "conflict":
            user_id = intent_dict.get("user_id", "USR-999")
            booking_ref = f"BK-WL-{random.randint(10000, 99999)}"
            waitlist_id = add_to_waitlist(
                provider_name=provider_name,
                appointment_time=appointment_time,
                user_id=user_id,
                booking_ref=booking_ref
            )
            waitlist_position = get_waitlist_position(
                provider_name=provider_name,
                appointment_time=appointment_time,
                user_id=user_id
            )

        # ── 5. Generate multilingual messaging ─────────────────────────────
        language = (intent_dict.get("language_detected") or "english").lower()
        use_gemini_env = os.getenv("USE_GEMINI", "false").lower() == "true"
        use_gemini = state.get("use_gemini", use_gemini_env)
        message = self._generate_booking_message_with_fallback(
            status=status,
            provider_name=provider_name,
            appointment_time=appointment_time,
            booking_id=booking_id,
            alt_slots=alt_slots,
            alt_provs=alt_provs,
            language=language,
            use_gemini=use_gemini
        )

        # ── 6. Assemble Output ────────────────────────────────────────────
        booking_output = BookingOutput(
            booking_id=booking_id,
            status=status,
            provider_name=provider_name,
            appointment_time=appointment_time,
            total_price=total_price,
            alternative_slots=alt_slots,
            alternative_providers=alt_provs,
            reminders_sent=reminders_sent,
            progress_updates=progress_updates,
            message=message,
            waitlist_id=waitlist_id,
            waitlist_position=waitlist_position,
            auto_rescheduled=auto_rescheduled
        )

        output_dict = booking_output.model_dump()
        reasoning_summary = (
            f"Booking {status} for {provider_name} at {appointment_time}. "
            f"ID: {booking_id}. Alternatives slots generated: {len(alt_slots)}. "
            f"Alternative providers suggested: {len(alt_provs)}."
        )
        if waitlist_id:
            reasoning_summary += f" Added to waitlist: {waitlist_id} at position {waitlist_position}."

        # ── 7. Generate Trace ─────────────────────────────────────────────
        trace = make_trace(
            step_name="booking",
            agent_name=self.name,
            input_data=booking_input.model_dump(),
            output_data=dict(output_dict),
            tool_called="check_booking_collision_and_confirm",
            start_time=start_time,
            status="fallback" if status == "conflict" else "success",
            reasoning_summary=reasoning_summary
        )

        state["booking"] = output_dict
        state["booking"]["trace"] = trace

        if "agent_trace" in state:
            state["agent_trace"].append(trace)

        return state

    # ── Helpers ────────────────────────────────────────────────────────────

    def _generate_booking_message_with_fallback(
        self,
        status: str,
        provider_name: str,
        appointment_time: str,
        booking_id: str | None,
        alt_slots: List[str],
        alt_provs: List[str],
        language: str,
        use_gemini: bool = False
    ) -> str:
        """
        Generate multilingual scheduling messaging.
        """
        prompt = f"""
You are the Booking notification engine for ServisAI Pakistan.
Write a polite client update message.

Booking Details:
- Status: {status}
- Provider Name: {provider_name}
- Requested Time: {appointment_time}
- Generated Booking ID: {booking_id}
- Alternative Slots (if conflict): {alt_slots}
- Alternative Providers (if conflict): {alt_provs}

Customer Language Preference: {language}

Instructions:
1. Explain the booking status:
   - If status is 'confirmed': Congratulate them on booking {provider_name} and confirm their time.
   - If status is 'conflict': Explain that {provider_name} is double-booked or busy at that exact hour, apologize, and clearly propose the alternative slots or alternative providers.
2. Write strictly in the requested language:
   - If 'urdu': Write in Urdu script (Arabic letters).
   - If 'roman_urdu' or 'mixed': Write in Roman Urdu (Urdu written in English letters).
   - If 'english' or 'unknown': Write in clean, professional English.
3. Keep the tone extremely polite, helpful, and respectful of their time.
4. Do not include markdown codeblocks or tags. Return only the notification text.
"""
        system_instruction = "You are a polite, helpful booking dispatcher for ServisAI Pakistan."

        preferred_prov = "gemini" if use_gemini else os.getenv("LLM_PROVIDER", "groq").lower()

        from utils.llm_provider import generate_llm_text
        res, actual_provider = generate_llm_text(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.3,
            max_tokens=300,
            preferred_provider=preferred_prov
        )

        if res and actual_provider != "none":
            return res

        # Deterministic Fallbacks
        if status == "confirmed":
            if language in ("roman_urdu", "mixed"):
                return (
                    f"Mubarak ho! Aapki booking confirm ho chuki hai. Aapka Booking ID: {booking_id} hai. "
                    f"Hamare verification partner {provider_name} {appointment_time} par pohnch jayenge. "
                    f"Humne aapko SMS par confirmation aur live tracking link bhej diya hai."
                )
            elif language == "urdu":
                return (
                    f"مبارک ہو! آپ کی بکنگ کی تصدیق ہو چکی ہے۔ آپ کا بکنگ ID: {booking_id} ہے۔ "
                    f"ہمارے پارٹنر {provider_name} وقت {appointment_time} پر پہنچ جائیں گے۔ "
                    f"ہم نے آپ کو ایس ایم ایس کے ذریعے تصدیقی لنک بھیج دیا ہے۔"
                )
            else:
                return (
                    f"Congratulations! Your booking is confirmed. Your Booking ID is {booking_id}. "
                    f"Our verified partner {provider_name} will arrive at {appointment_time}. "
                    f"We have sent a SMS confirmation and live progress tracking receipt to your mobile."
                )
        else: # conflict
            alt_slots_str = ", ".join(alt_slots) if alt_slots else "later today"
            alt_provs_str = " or ".join(alt_provs) if alt_provs else "another partner"
            if language in ("roman_urdu", "mixed"):
                return (
                    f"Hamein afsos hai, par {provider_name} {appointment_time} par pehle se book hain. "
                    f"Kya aap in alternative times par comfortable hain: {alt_slots_str}? "
                    f"Ya hum aapko hamare doosre top partner: {alt_provs_str} assign kar dein? "
                    f"Hamein reply karein taake hum foran adjust kar sakein."
                )
            elif language == "urdu":
                return (
                    f"ہمیں معذرت ہے، لیکن {provider_name} اس وقت {appointment_time} پر پہلے سے بک ہیں۔ "
                    f"کیا آپ ان متبادل اوقات پر بکنگ چاہتے ہیں: {alt_slots_str}؟ "
                    f"یا ہم آپ کو ہمارے دوسرے پارٹنر: {alt_provs_str} تجویز کریں؟ "
                    f"ہمیں جواب دیں تاکہ ہم بکنگ کر سکیں۔"
                )
            else:
                return (
                    f"We apologize, but {provider_name} has a scheduling conflict at {appointment_time}. "
                    f"Would you be open to these alternative time slots: {alt_slots_str}? "
                    f"Alternatively, we can assign you to our other top-rated partner(s): {alt_provs_str}. "
                    f"Please reply with your preference so we can lock in the slot."
                )

    def _error_state(
        self,
        state: Dict[str, Any],
        start_time: float,
        input_snapshot: Any,
        error_msg: str,
    ) -> Dict[str, Any]:
        """Record error state in booking block."""
        trace = make_trace(
            step_name="booking",
            agent_name=self.name,
            input_data=input_snapshot,
            output_data={},
            tool_called="booking_error_fallback",
            start_time=start_time,
            status="error",
            reasoning_summary=f"Booking agent error: {error_msg}",
            errors=[error_msg]
        )
        state["booking"] = {
            "status": "error",
            "error": error_msg,
            "trace": trace
        }
        if "agent_trace" in state:
            state["agent_trace"].append(trace)
        return state
