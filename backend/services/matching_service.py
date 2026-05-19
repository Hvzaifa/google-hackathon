from db.supabase_client import supabase


def get_reputation_adjustment(provider_name: str) -> dict:
    if supabase is None:
        return {
            "reputation_score": 0.75,
            "future_matching_impact": 0
        }

    result = (
        supabase
        .table("provider_reputation")
        .select("*")
        .eq("provider_name", provider_name)
        .execute()
    )

    if not result.data:
        return {
            "reputation_score": 0.75,
            "future_matching_impact": 0
        }

    row = result.data[0]

    return {
        "reputation_score": row.get("reputation_score", 0.75),
        "future_matching_impact": row.get("future_matching_impact", 0)
    }


def normalize(value, min_value, max_value):
    if max_value == min_value:
        return 1.0
    return (value - min_value) / (max_value - min_value)


def calculate_budget_score(provider, budget_sensitivity):
    """
    Lower base_rate preferred if user is highly budget sensitive.
    """

    base_rate = provider.get("base_rate", 500)

    if budget_sensitivity == "high":
        if base_rate <= 400:
            return 1.0
        elif base_rate <= 600:
            return 0.7
        return 0.3

    if budget_sensitivity == "medium":
        if base_rate <= 700:
            return 1.0
        return 0.6

    return 1.0 


def calculate_complexity_score(provider, job_complexity):
    provider_level = provider.get("complexity_level", "basic")

    hierarchy = {
        "basic": 1,
        "intermediate": 2,
        "complex": 3
    }

    provider_score = hierarchy.get(provider_level, 1)
    required_score = hierarchy.get(job_complexity, 1)

    if provider_score >= required_score:
        return 1.0

    return 0.4
        

def rank_providers(providers, intent):
    if not providers:
        return {
            "status": "no_providers",
            "selected_provider": None,
            "top_matches": [],
            "ranking_summary": "No providers available."
        }

    normalized_providers = []

    for provider in providers:
        normalized = {
            **provider,
            "name": provider.get("name", "Unknown Provider"),
            "rating": provider.get("rating", 0),
            "review_count": provider.get("review_count", 0),
            "distance_km": provider.get("distance_km", 999),
            "review_recency": provider.get("review_recency", 0.5),
            "on_time_score": provider.get("on_time_score", 0.5),
            "cancellation_rate": provider.get("cancellation_rate", 0.5),
            "base_rate": provider.get("base_rate", 500),
            "per_km_rate": provider.get("per_km_rate", 30),
            "complexity_level": provider.get("complexity_level", "intermediate"),
        }

        normalized_providers.append(normalized)

    providers = normalized_providers

    distances = [p.get("distance_km", 3.0) for p in providers]
    ratings = [p.get("rating", 0) for p in providers]
    reviews = [p.get("review_count", 0) for p in providers]

    min_distance = min(distances)
    max_distance = max(distances)

    min_rating = min(ratings)
    max_rating = max(ratings)

    min_reviews = min(reviews)
    max_reviews = max(reviews)

    ranked = []

    for provider in providers:

        distance_score = 1 - normalize(
            provider.get("distance_km", 3.0),
            min_distance,
            max_distance
        )

        rating_score = normalize(
            provider.get("rating", 0),
            min_rating,
            max_rating
        )

        review_score = normalize(
            provider.get("review_count", 0),
            min_reviews,
            max_reviews
        )

        review_recency_score = provider.get(
            "review_recency",
            0.8
        )

        on_time_score = provider.get("on_time_score", 0.8)

        cancellation_score = 1 - provider.get(
            "cancellation_rate",
            0.1
        )

        budget_score = calculate_budget_score(
            provider,
            intent.get("budget_sensitivity")
        )

        complexity_score = calculate_complexity_score(
            provider,
            intent.get("job_complexity")
        )

        reputation = get_reputation_adjustment(
            provider.get("name")
        )

        reputation_score = reputation["reputation_score"]
        future_matching_impact = reputation["future_matching_impact"]

        final_score = (
            distance_score * 0.20 +
            rating_score * 0.16 +
            review_score * 0.09 +
            review_recency_score * 0.08 +
            on_time_score * 0.14 +
            cancellation_score * 0.09 +
            budget_score * 0.09 +
            complexity_score * 0.06 +
            reputation_score * 0.07 +
            future_matching_impact * 0.02
        )

        provider["matching_scores"] = {
            "distance_score": round(distance_score, 2),
            "rating_score": round(rating_score, 2),
            "review_score": round(review_score, 2),
            "review_recency_score": round(review_recency_score, 2),
            "on_time_score": round(on_time_score, 2),
            "cancellation_score": round(cancellation_score, 2),
            "budget_score": round(budget_score, 2),
            "complexity_score": round(complexity_score, 2),
            "reputation_score": round(reputation_score, 2),
            "future_matching_impact": round(future_matching_impact, 2),
        }

        provider["final_matching_score"] = round(final_score, 3)

        ranked.append(provider)

    ranked.sort(
        key=lambda x: x["final_matching_score"],
        reverse=True
    )

    winner = ranked[0]

    summary = (
        f"{winner['name']} selected with "
        f"a matching score of "
        f"{winner['final_matching_score']}. "
        f"The provider ranked highest due to "
        f"strong distance proximity, "
        f"high reliability, "
        f"good budget compatibility, "
        f"and suitable experience level."
    )

    return {
        "status": "provider_selected",

        "decision_factors": [
            "distance",
            "rating",
            "review_count",
            "review_recency",
            "on_time_score",
            "cancellation_rate",
            "budget_compatibility",
            "complexity_compatibility",
            "provider_reputation_memory"
        ],

        "selected_provider": winner,

        "top_matches": ranked[:3],

        "ranking_summary": summary
    }