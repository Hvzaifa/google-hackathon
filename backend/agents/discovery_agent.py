from tools.maps_tool import find_nearby_providers


class DiscoveryAgent:
    name="DiscoveryAgent"

    def run(self, state:dict) -> dict:
        intent = state.get("intent", {})

        service_type = intent.get("service_type")
        location = intent.get("location")

        if not service_type or not location:
            state["discovery"] = {
                "status": "skipped",
                "reason": "Missing service_type or location",
                "providers": []
            }
            return state
        
        discovery_result = find_nearby_providers(
            location=location,
            service_type=service_type
        )

        providers = discovery_result.get("providers", [])

        state["discovery"] = {
            "status": "providers_found" if providers else "no_providers",
            "service_type": service_type,
            "location": location,
            "source": discovery_result.get("source"),
            "fallback_used": discovery_result.get("fallback_used"),
            "fallback_reason": discovery_result.get("fallback_reason"),
            "origin": discovery_result.get("origin"),
            "providers_count": len(providers),
            "providers": providers
        }

        state["providers"] = providers

        return state