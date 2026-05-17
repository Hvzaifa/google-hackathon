"""
Multi-factor scoring tool for the Matching Agent.

All scoring math is DETERMINISTIC Python — no LLM calls.
Each factor produces a 0.0–1.0 sub-score. The overall score is a
weighted average, with weights adjusted dynamically based on urgency
and budget sensitivity from the user's intent.

Factor weights (default):
    distance        0.20
    rating          0.20
    review_recency  0.10
    reliability     0.20
    price_fit       0.15
    specialization  0.10
    availability    0.05   (binary gate — unavailable providers get 0 overall)
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

from schemas.matching_schema import (
    IntentData,
    ProviderCandidate,
    ScoreBreakdown,
    ScoredProvider
)

# ── Default weights ─────────────────────────────────────────────────────────
DEFAULT_WEIGHTS: Dict[str, float] = {
    "distance":          0.15,
    "rating":            0.15,
    "review_recency":    0.08,
    "on_time_score":     0.12,
    "cancellation_risk": 0.10,
    "risk_score":        0.08,
    "price_fit":         0.12,
    "specialization":    0.10,
    "user_preference":   0.05,
    "availability":      0.05,
}


# ── Weight adjustments per intent signal ────────────────────────────────────

def _adjust_weights(intent: IntentData) -> Dict[str, float]:
    """
    Return context-adjusted weights based on user intent signals.
    """
    w = DEFAULT_WEIGHTS.copy()

    # --- Urgency ---
    if intent.urgency in ("urgent", "same_day"):
        w["distance"] += 0.08
        w["on_time_score"] += 0.05
        w["cancellation_risk"] += 0.03
        w["review_recency"] -= 0.05
        w["price_fit"] -= 0.05
        w["specialization"] -= 0.03

    # --- Budget sensitivity ---
    if intent.budget_sensitivity == "high":
        w["price_fit"] += 0.10
        w["rating"] -= 0.05
        w["distance"] -= 0.05
    elif intent.budget_sensitivity == "low":
        w["price_fit"] -= 0.05
        w["rating"] += 0.03
        w["on_time_score"] += 0.01
        w["cancellation_risk"] += 0.01

    # --- Job complexity ---
    if intent.job_complexity == "complex":
        w["specialization"] += 0.08
        w["on_time_score"] += 0.02
        w["cancellation_risk"] += 0.02
        w["price_fit"] -= 0.06
        w["distance"] -= 0.06

    # Clamp negatives, then normalise to sum = 1.0
    w = {k: max(v, 0.01) for k, v in w.items()}
    total = sum(w.values())
    w = {k: v / total for k, v in w.items()}

    return w


# ── Individual factor scorers ───────────────────────────────────────────────

def _score_distance(distance_km: float) -> float:
    """
    Exponential decay: score = e^(-0.15 * distance_km).
    0 km → 1.0, 5 km → ~0.47, 10 km → ~0.22, 20 km → ~0.05.
    """
    return math.exp(-0.15 * distance_km)


def _score_rating(rating: float) -> float:
    """Normalise 0-5 rating to 0.0-1.0."""
    return min(max(rating / 5.0, 0.0), 1.0)


def _score_review_recency(recency: float) -> float:
    """
    Already a 0.0-1.0 float from discovery.
    Apply slight boost: emphasise the 0.7–1.0 range.
    """
    return min(max(recency, 0.0), 1.0)


def _score_on_time(on_time: float) -> float:
    """0.0–1.0 passthrough with clamp."""
    return min(max(on_time, 0.0), 1.0)


def _score_cancellation_risk(cancel_rate: float) -> float:
    """Lower cancellation rate = higher score. cancel_rate is 0.0–1.0."""
    return 1.0 - min(max(cancel_rate, 0.0), 1.0)


def _score_risk(risk_score: float) -> float:
    """Lower risk_score value = higher match score (risk_score 0 = safest)."""
    return 1.0 - min(max(risk_score, 0.0), 1.0)


def _score_user_preference(provider: ProviderCandidate, preferences: List[str]) -> float:
    """
    Score how many user preferences the provider satisfies.
    Preferences are free-text strings from intent (e.g. 'female technician', 'certified', 'experienced').
    Match by checking if any preference keyword appears in provider.name,
    provider.specialization, or provider.service_type (case-insensitive).
    Returns 1.0 if all preferences matched, 0.5 if some, 0.2 if none.
    If no preferences given, return 0.7 (neutral).
    """
    if not preferences:
        return 0.7
    provider_text = " ".join(filter(None, [
        provider.name, provider.specialization, provider.service_type
    ])).lower()
    matched = sum(1 for p in preferences if p.lower() in provider_text)
    if matched == len(preferences):
        return 1.0
    elif matched > 0:
        return 0.5
    return 0.2


def _score_price_fit(
    base_rate: int,
    per_km_rate: int,
    distance_km: float,
    budget_sensitivity: str,
    all_estimated_costs: List[float],
) -> float:
    """
    Evaluate how well a provider's estimated cost aligns with budget needs.
    """
    estimated_cost = base_rate + per_km_rate * distance_km

    if not all_estimated_costs or len(all_estimated_costs) < 2:
        # Cannot compare — neutral score
        return 0.5

    min_cost = min(all_estimated_costs)
    max_cost = max(all_estimated_costs)
    cost_range = max_cost - min_cost

    if cost_range == 0:
        return 0.8  # All same price — good fit for everyone

    # Normalised position: 0 = cheapest, 1 = most expensive
    normalised = (estimated_cost - min_cost) / cost_range

    if budget_sensitivity == "high":
        # Cheaper is better — linear inverse
        return 1.0 - normalised
    elif budget_sensitivity == "medium":
        # Mid-range is ideal — bell-curve-like
        return 1.0 - abs(normalised - 0.5) * 2.0
    else:
        # Low / unknown — slight mid-range preference, but almost flat
        return 0.7 + 0.3 * (1.0 - abs(normalised - 0.5) * 2.0)


def _score_specialization(
    provider_complexity: str, job_complexity: str
) -> float:
    """
    How well the provider's complexity level matches the job.
    """
    levels = {"basic": 0, "intermediate": 1, "complex": 2}

    if provider_complexity not in levels or job_complexity not in levels:
        return 0.6  # Unknown → neutral

    p = levels[provider_complexity]
    j = levels[job_complexity]

    if p == j:
        return 1.0
    elif p > j:
        return 0.8  # Overqualified
    else:
        return 0.4  # Underqualified


def _score_availability(available: bool) -> float:
    """Binary: 1.0 if available, 0.0 if not."""
    return 1.0 if available else 0.0


# ── Main scoring entry point ───────────────────────────────────────────────

def multi_factor_scoring(
    providers: List[ProviderCandidate],
    intent: IntentData,
) -> List[ScoredProvider]:
    """
    Score and rank all providers using deterministic multi-factor analysis.
    """
    if not providers:
        return []

    weights = _adjust_weights(intent)

    # Pre-compute estimated costs for price_fit normalisation
    estimated_costs: List[float] = [
        p.base_rate + p.per_km_rate * p.distance_km for p in providers
    ]

    scored: List[Tuple[float, ScoredProvider]] = []

    for idx, provider in enumerate(providers):
        # --- Compute individual factor scores ---
        dist_score = _score_distance(provider.distance_km)
        rating_score = _score_rating(provider.rating)
        recency_score = _score_review_recency(provider.review_recency)
        ontime_score = _score_on_time(provider.on_time_score)
        cancel_score = _score_cancellation_risk(provider.cancellation_rate)
        risk_score_val = _score_risk(provider.risk_score)
        price_score = _score_price_fit(
            provider.base_rate,
            provider.per_km_rate,
            provider.distance_km,
            intent.budget_sensitivity,
            estimated_costs,
        )
        spec_score = _score_specialization(
            provider.complexity_level, intent.job_complexity
        )
        preference_score = _score_user_preference(provider, intent.user_preferences)
        avail_score = _score_availability(provider.available)

        breakdown = ScoreBreakdown(
            distance=round(dist_score, 4),
            rating=round(rating_score, 4),
            review_recency=round(recency_score, 4),
            on_time_score=round(ontime_score, 4),
            cancellation_risk=round(cancel_score, 4),
            risk_score=round(risk_score_val, 4),
            price_fit=round(price_score, 4),
            specialization=round(spec_score, 4),
            user_preference=round(preference_score, 4),
            availability=round(avail_score, 4),
        )

        # --- Weighted sum ---
        if avail_score == 0.0:
            # Unavailable providers get 0 overall regardless of other factors
            overall = 0.0
        else:
            overall = (
                weights["distance"] * dist_score
                + weights["rating"] * rating_score
                + weights["review_recency"] * recency_score
                + weights["on_time_score"] * ontime_score
                + weights["cancellation_risk"] * cancel_score
                + weights["risk_score"] * risk_score_val
                + weights["price_fit"] * price_score
                + weights["specialization"] * spec_score
                + weights["user_preference"] * preference_score
                + weights["availability"] * avail_score
            )

        overall = round(min(max(overall, 0.0), 1.0), 4)

        # --- Build reasoning string ---
        reasoning = _build_reasoning(provider, breakdown, weights, overall)

        # Preserve original provider dict for downstream agents
        provider_dict = provider.model_dump(exclude_none=True)

        scored.append(
            (
                overall,
                provider.name,
                breakdown,
                reasoning,
                provider_dict,
            )
        )

    # Sort descending by overall score
    scored.sort(key=lambda x: x[0], reverse=True)

    # Assign ranks and cap at 5
    result: List[ScoredProvider] = []
    for rank, (overall, name, breakdown, reasoning, provider_dict) in enumerate(scored[:5], start=1):
        result.append(
            ScoredProvider(
                name=name,
                overall_score=overall,
                score_breakdown=breakdown,
                rank=rank,
                reasoning=reasoning,
                provider_data=provider_dict,
            )
        )

    return result


# ── Reasoning builder ───────────────────────────────────────────────

def _build_reasoning(
    provider: ProviderCandidate,
    breakdown: ScoreBreakdown,
    weights: Dict[str, float],
    overall: float,
) -> str:
    """Produce a concise, human-readable reasoning string for this provider."""
    if not provider.available:
        return f"{provider.name} is currently unavailable — excluded from ranking."

    factor_scores = {
        "distance": breakdown.distance,
        "rating": breakdown.rating,
        "review_recency": breakdown.review_recency,
        "on_time_score": breakdown.on_time_score,
        "cancellation_risk": breakdown.cancellation_risk,
        "risk_score": breakdown.risk_score,
        "price_fit": breakdown.price_fit,
        "specialization": breakdown.specialization,
        "user_preference": breakdown.user_preference,
    }

    # Weighted contribution
    contributions = {
        k: round(factor_scores[k] * weights.get(k, 0), 4)
        for k in factor_scores
    }

    sorted_factors = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
    strengths = [f[0] for f in sorted_factors[:2]]
    weakness = sorted_factors[-1][0] if sorted_factors else "none"

    parts = [
        f"Score {overall:.2f}.",
        f"Strongest in {strengths[0]} ({factor_scores[strengths[0]]:.2f})",
    ]
    if len(strengths) > 1:
        parts.append(f"and {strengths[1]} ({factor_scores[strengths[1]]:.2f}).")
    else:
        parts[-1] += "."

    if factor_scores.get(weakness, 1.0) < 0.6:
        parts.append(f"Weaker on {weakness} ({factor_scores[weakness]:.2f}).")

    return " ".join(parts)
