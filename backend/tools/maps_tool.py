import os
import json
import random
from pathlib import Path
import googlemaps
from geopy.distance import geodesic
from dotenv import load_dotenv

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY) if GOOGLE_MAPS_API_KEY else None

def load_mock_providers(service_type: str, location: str | None = None) -> list:
    file_path = Path("data/mock_providers.json")

    if not file_path.exists():
        file_path = Path("backend/data/mock_providers.json")

    with open(file_path, "r") as f:
        providers = json.load(f)

    service = service_type.lower()
    matched = [
        p for p in providers
        if service in p["service_type"].lower()
        or p["service_type"].lower() in service
        or service.split()[0] in p["service_type"].lower()
    ]

    return matched[:6]


def find_nearby_providers(location: str, service_type: str) -> dict:
    """
    Finds nearby providers using Google Maps.
    Falls back to mock data if Maps fails or returns no usable result.
    """

    if not gmaps:
        return {
            "source": "mock_fallback",
            "fallback_used": True,
            "fallback_reason": "GOOGLE_MAPS_API_KEY missing",
            "providers": load_mock_providers(service_type, location),
        }

    try:
        geocode_result = gmaps.geocode(location)

        if not geocode_result:
            return {
                "source": "mock_fallback",
                "fallback_used": True,
                "fallback_reason": "Geocoding returned no results",
                "providers": load_mock_providers(service_type, location),
            }

        origin_lat = geocode_result[0]["geometry"]["location"]["lat"]
        origin_lng = geocode_result[0]["geometry"]["location"]["lng"]
        origin = (origin_lat, origin_lng)

        all_results = []

        for radius in [5000, 10000, 15000]:
            places_result = gmaps.places_nearby(
                location=origin,
                radius=radius,
                keyword=service_type,
                type="establishment",
            )

            all_results = places_result.get("results", [])

            if len(all_results) >= 3:
                break

        if not all_results:
            return {
                "source": "mock_fallback",
                "fallback_used": True,
                "fallback_reason": "Places API returned no providers",
                "providers": load_mock_providers(service_type, location),
            }

        providers = []

        for place in all_results[:6]:
            provider_lat = place["geometry"]["location"]["lat"]
            provider_lng = place["geometry"]["location"]["lng"]

            distance_km = round(
                geodesic(origin, (provider_lat, provider_lng)).km,
                2
            )

            providers.append({
                "name": place.get("name"),
                "service_type": service_type,
                "address": place.get("vicinity", ""),
                "lat": provider_lat,
                "lng": provider_lng,
                "rating": place.get("rating", 3.5),
                "review_count": place.get("user_ratings_total", 0),
                "distance_km": distance_km,
                "available": True,
                "source": "google_maps",
                "place_id": place.get("place_id"),
                "review_recency": round(random.uniform(0.65, 0.98), 2),
                "on_time_score": round(random.uniform(0.70, 0.97), 2),
                "cancellation_rate": round(random.uniform(0.02, 0.25), 2),
                "base_rate": random.choice([400, 500, 600, 700]),
                "per_km_rate": random.choice([20, 25, 30, 35]),
                "complexity_level": "intermediate"
            })

        return {
            "source": "google_maps",
            "fallback_used": False,
            "fallback_reason": None,
            "origin": {
                "lat": origin_lat,
                "lng": origin_lng,
                "location": location
            },
            "providers": providers,
        }

    except Exception as e:
        return {
            "source": "mock_fallback",
            "fallback_used": True,
            "fallback_reason": str(e),
            "providers": load_mock_providers(service_type, location),
        }