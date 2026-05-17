"""
Deterministic reputation calculation and dispute resolution engine.
Processes feedback, computes new average ratings, and applies resolution protocols.
"""

from typing import Dict, Any, List, Tuple


def calculate_new_reputation(
    current_rating: float,
    current_review_count: int,
    new_user_rating: int
) -> Tuple[float, int]:
    """
    Compute updated provider reputation score using running moving average.
    Returns: Tuple of (new_rating, new_review_count)
    """
    # Ensure values are within logical bounds
    rating = min(max(float(current_rating), 0.0), 5.0)
    count = max(int(current_review_count), 0)
    user_val = min(max(int(new_user_rating), 1), 5)

    new_count = count + 1
    new_rating = round(((rating * count) + user_val) / new_count, 2)
    
    return new_rating, new_count


def process_dispute_resolution(
    rating: int,
    review_text: str,
    issue_reported: bool,
    dispute_type: str = "general"
) -> Tuple[str, List[str], str]:
    """
    Processes post-service feedback and determines dispute handling path.
    Supports dispute types: general | no_show | cancellation | price_disagreement | overrun.
    """
    review = (review_text or "").lower()
    
    # Specific dispute type handling overrides sit ABOVE is_negative check
    if dispute_type == "no_show":
        actions = [
            "PKR 500 compensation coupon issued to customer",
            "strike registered on provider profile",
            "automated rescheduling options triggered"
        ]
        return "dispute_resolved", actions, ""
        
    elif dispute_type == "cancellation":
        actions = [
            "Full booking deposit refund initiated to source account",
            "provider cancellation fee penalized",
            "warning notification sent to provider"
        ]
        return "dispute_resolved", actions, ""
        
    elif dispute_type == "price_disagreement":
        actions = [
            "goodwill compensation credit of PKR 500 added to customer wallet",
            "price verification ticket closed",
            "provider advised on billing transparency"
        ]
        return "dispute_resolved", actions, ""
        
    elif dispute_type == "overrun":
        actions = [
            "Warning issued to service partner regarding time limits",
            "10% booking fee discount credit added to customer wallet"
        ]
        return "dispute_resolved", actions, ""

    is_negative = (rating <= 2) or issue_reported

    if not is_negative:
        return "reputation_updated", ["partner ranking updated", "customer feedback survey closed"], ""

    # Severe dispute escalation triggers for general dispute
    escalation_triggers = [
        "abuse", "theft", "stole", "damage", "fight", "broke",
        "gaali", "badtameezi", "maar", "chor", "chori", "police"
    ]
    
    is_severe = any(trigger in review for trigger in escalation_triggers)
    
    if is_severe:
        actions = [
            "dispute flagged for manual verification",
            "provider account temporarily suspended",
            "escalated to operations safety desk for Urdu call verification"
        ]
        return "dispute_escalated", actions, "Severe behavior, property damage, or safety risk reported in Urdu/English review."
    
    # Minor dispute auto-resolved
    actions = [
        "apology message dispatched",
        "PKR 300 compensation credit added to user wallet",
        "warning notification sent to service provider regarding punctuality/quality"
    ]
    return "dispute_resolved", actions, ""
