"""
Matching Agent — Agent 3 of the ServisAI pipeline.

Consumes provider candidates from Discovery (state["providers"]) and
intent context (state["intent"]) to produce a ranked shortlist of 3–5
providers using deterministic multi-factor scoring.

No LLM calls are made here. All intelligence lives in scoring_tool.py.

State contract
--------------
Input  (reads):  state["providers"], state["intent"]
Output (writes): state["matching"]
Trace  (appends): appended to state["agent_trace"] if it exists,
                  otherwise written to state["matching"]["trace"]
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

from schemas.matching_schema import (
    IntentData,
    MatchingInput,
    MatchingOutput,
    ProviderCandidate,
    ScoredProvider,
)
from tools.scoring_tool import multi_factor_scoring
from utils.trace import make_trace


class MatchingAgent:
    """
    Ranks provider candidates by multi-factor score and returns a
    shortlist of the top 3–5 matches.

    Usage
    -----
    >>> agent = MatchingAgent()
    >>> state = agent.run(state)
    >>> state["matching"]   # ranked providers + trace
    """

    name: str = "MatchingAgent"

    # Fewer than this many scored providers → status = "fallback"
    FALLBACK_THRESHOLD: int = 2

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the matching step.

        Parameters
        ----------
        state : dict
            Pipeline state carrying at minimum:
              - "providers" : list[dict]  — raw candidates from Discovery
              - "intent"    : dict        — structured intent from Intent Agent

        Returns
        -------
        dict
            Updated state with "matching" key populated.
        """
        start_time = time.time()

        # ── 1. Extract and validate inputs ────────────────────────────────
        raw_providers: List[dict] = state.get("providers", [])
        raw_intent: dict = state.get("intent", {})

        try:
            matching_input = self._parse_input(raw_providers, raw_intent)
        except Exception as exc:
            return self._error_state(
                state,
                start_time,
                input_snapshot={"providers": raw_providers, "intent": raw_intent},
                error_msg=str(exc),
            )

        providers = matching_input.providers
        intent = matching_input.intent

        # ── 2. Early-exit: no providers at all ────────────────────────────
        if not providers:
            return self._write_result(
                state,
                start_time,
                input_data=matching_input.model_dump(),
                ranked=[],
                total=0,
                available=0,
                status="fallback",
                reasoning_summary=(
                    "No provider candidates received from Discovery. "
                    "Cannot rank without candidates."
                ),
            )

        # ── 3. Count available vs total ───────────────────────────────────
        available_count = sum(1 for p in providers if p.available)
        total_count = len(providers)

        # ── 4. All unavailable ────────────────────────────────────────────
        if available_count == 0:
            return self._write_result(
                state,
                start_time,
                input_data=matching_input.model_dump(),
                ranked=[],
                total=total_count,
                available=0,
                status="fallback",
                reasoning_summary=(
                    f"All {total_count} provider(s) are currently unavailable. "
                    "No ranking possible — try again later or expand search radius."
                ),
            )

        # ── 5. Run multi-factor scoring ───────────────────────────────────
        try:
            ranked: List[ScoredProvider] = multi_factor_scoring(providers, intent)
        except Exception as exc:
            return self._error_state(
                state,
                start_time,
                input_snapshot=matching_input.model_dump(),
                error_msg=f"Scoring tool error: {exc}",
            )

        # ── 6. Determine status ───────────────────────────────────────────
        # Filter to only available providers in the ranked list (0-score ones
        # are still present but ordered last)
        ranked_available = [sp for sp in ranked if sp.overall_score > 0.0]
        status = (
            "fallback"
            if len(ranked_available) < self.FALLBACK_THRESHOLD
            else "success"
        )

        reasoning_summary = self._build_summary(
            ranked_available, intent, total_count, available_count, status
        )

        return self._write_result(
            state,
            start_time,
            input_data=matching_input.model_dump(),
            ranked=ranked,
            total=total_count,
            available=available_count,
            status=status,
            reasoning_summary=reasoning_summary,
        )

    # ── Private helpers ────────────────────────────────────────────────────

    def _parse_input(
        self, raw_providers: List[dict], raw_intent: dict
    ) -> MatchingInput:
        """
        Coerce raw dicts into validated Pydantic models.
        Missing/null fields fall back to safe defaults defined in the schema.
        """
        validated_providers: List[ProviderCandidate] = []
        for p in raw_providers:
            # Normalise the "available" key — discovery may use True/False/None
            if "available" not in p:
                p = {**p, "available": True}
            # Fill in missing scoring fields with sensible defaults so the
            # schema validator doesn't reject partial mock/maps providers.
            defaults = {
                "distance_km": 5.0,
                "on_time_score": 0.80,
                "cancellation_rate": 0.10,
                "review_recency": 0.75,
                "complexity_level": "intermediate",
                "base_rate": 500,
                "per_km_rate": 25,
                "rating": 3.5,
                "review_count": 0,
            }
            merged = {**defaults, **{k: v for k, v in p.items() if v is not None}}
            validated_providers.append(ProviderCandidate(**merged))

        validated_intent = IntentData(
            service_type=raw_intent.get("service_type"),
            urgency=raw_intent.get("urgency", "unknown"),
            budget_sensitivity=raw_intent.get("budget_sensitivity", "unknown"),
            job_complexity=raw_intent.get("job_complexity", "unknown"),
            user_preferences=raw_intent.get("user_preferences", []),
            constraints=raw_intent.get("constraints", []),
        )

        return MatchingInput(providers=validated_providers, intent=validated_intent)

    def _build_summary(
        self,
        ranked_available: List[ScoredProvider],
        intent: IntentData,
        total: int,
        available: int,
        status: str,
    ) -> str:
        """Concise human-readable summary of the ranking decision."""
        if status == "fallback":
            return (
                f"Only {len(ranked_available)} available provider(s) found from "
                f"{total} candidates. Fallback mode — limited choice returned."
            )

        top = ranked_available[0] if ranked_available else None
        signals = []
        if intent.urgency in ("urgent", "same_day"):
            signals.append("urgency")
        if intent.budget_sensitivity == "high":
            signals.append("budget sensitivity")
        if intent.job_complexity == "complex":
            signals.append("job complexity")

        signal_str = (
            f"Weights adjusted for {', '.join(signals)}. " if signals else ""
        )
        top_str = (
            f"Top match: {top.name} (score {top.overall_score:.2f}). "
            if top
            else ""
        )

        return (
            f"{signal_str}Ranked {len(ranked_available)} of {available} available "
            f"providers from {total} candidates. {top_str}"
            f"Scoring factors: distance, rating, reliability, price fit, specialization."
        )

    def _write_result(
        self,
        state: Dict[str, Any],
        start_time: float,
        input_data: Any,
        ranked: List[ScoredProvider],
        total: int,
        available: int,
        status: str,
        reasoning_summary: str,
    ) -> Dict[str, Any]:
        """Serialise output, write to state, and append trace entry."""
        output = MatchingOutput(
            status=status,
            ranked_providers=ranked,
            total_candidates=total,
            available_candidates=available,
            reasoning_summary=reasoning_summary,
        )
        output_dict = output.model_dump()

        trace = make_trace(
            step_name="matching",
            agent_name=self.name,
            input_data=input_data,
            output_data=output_dict,
            tool_called="multi_factor_scoring",
            start_time=start_time,
            status=status,
            reasoning_summary=reasoning_summary,
        )

        state["matching"] = output_dict
        state["matching"]["trace"] = trace

        # Also append to shared trace list if it already exists
        if "agent_trace" in state:
            state["agent_trace"].append(trace)

        return state

    def _error_state(
        self,
        state: Dict[str, Any],
        start_time: float,
        input_snapshot: Any,
        error_msg: str,
    ) -> Dict[str, Any]:
        """Write an error result to state."""
        return self._write_result(
            state,
            start_time,
            input_data=input_snapshot,
            ranked=[],
            total=0,
            available=0,
            status="error",
            reasoning_summary=f"Matching agent encountered an error: {error_msg}",
        )
