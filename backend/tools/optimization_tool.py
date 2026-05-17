"""
Provider Optimization and Demand Forecasting module.
Tracks provider workloads and monthly earnings to apply workload-balancing tiebreakers,
opportunity fairness scoring, and demand-based surge recommendations.
"""
from __future__ import annotations
import datetime
from typing import Dict, List, Any
from schemas.matching_schema import ScoredProvider

# Global in-memory list of booking history records
_booking_history: List[dict] = []

def record_booking(provider_name: str, total_price: float, timestamp: str | None = None) -> None:
    """Record a completed booking for workload tracking."""
    if not timestamp:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    _booking_history.append({
        "provider_name": provider_name,
        "total_price": float(total_price),
        "timestamp": timestamp
    })

def apply_workload_tiebreaker(scored_providers: List[ScoredProvider]) -> List[ScoredProvider]:
    """
    Apply workload earnings fairness tiebreaker sorting.
    If two providers have the same overall_score (rounded to 2 decimal places),
    the provider with LOWER monthly earnings must be ranked HIGHER.
    """
    def get_monthly_earnings(name: str) -> float:
        # Sum all recorded earnings in _booking_history
        return sum(b["total_price"] for b in _booking_history if b["provider_name"] == name)

    # Sort using stable sorts:
    # First: by earnings (ascending)
    scored_sorted = sorted(scored_providers, key=lambda x: get_monthly_earnings(x.name))
    # Second: by overall_score (descending, rounded to 2 decimal places)
    scored_sorted.sort(key=lambda x: round(x.overall_score, 2), reverse=True)

    # Reassign ranks based on final sort order
    for idx, provider in enumerate(scored_sorted):
        provider.rank = idx + 1

    return scored_sorted

def get_opportunity_fairness_index() -> float:
    """
    Returns an opportunity fairness score between 0.0 (unfair/skewed) and 1.0 (perfectly fair/equal).
    Derived from standard deviation of earnings across all providers present in history.
    """
    earnings: Dict[str, float] = {}
    for b in _booking_history:
        p = b["provider_name"]
        earnings[p] = earnings.get(p, 0.0) + b["total_price"]

    if not earnings:
        return 1.0

    vals = list(earnings.values())
    if len(vals) <= 1:
        return 1.0

    mean = sum(vals) / len(vals)
    if mean == 0:
        return 1.0

    variance = sum((x - mean) ** 2 for x in vals) / len(vals)
    std_dev = variance ** 0.5
    
    # 1.0 - (std_dev / mean) coefficient of variation metric, clamped between 0 and 1
    score = 1.0 - (std_dev / mean)
    return float(max(min(score, 1.0), 0.0))

def get_demand_forecast(service_type: str) -> Dict[str, Any]:
    """
    Return forecasted demand level, surge multiplier recommendation, and reasoning context.
    """
    now = datetime.datetime.now()
    is_ac = "ac" in service_type.lower() or "cooling" in service_type.lower()
    is_peak_hour = 12 <= now.hour <= 17

    if is_ac and is_peak_hour:
        return {
            "service_type": service_type,
            "forecasted_demand": "high",
            "surge_multiplier": 1.25,
            "reason": "Peak summer afternoon hours for AC cooling demand"
        }
    elif is_peak_hour:
        return {
            "service_type": service_type,
            "forecasted_demand": "medium",
            "surge_multiplier": 1.10,
            "reason": "Standard peak afternoon business hours"
        }
    else:
        return {
            "service_type": service_type,
            "forecasted_demand": "low",
            "surge_multiplier": 1.00,
            "reason": "Off-peak hours"
        }
