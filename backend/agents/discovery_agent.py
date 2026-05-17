import time
from tools.maps_tool import find_nearby_providers
from utils.trace import make_trace


class DiscoveryAgent:
    name = "DiscoveryAgent"

    def run(self, state: dict) -> dict:
        start_time = time.time()
        providers = []
        
        intent = state.get("intent", {})

        service_type = intent.get("service_type")
        location = intent.get("location")

        if not service_type or not location:
            state["discovery"] = {
                "status": "skipped",
                "reason": "Missing service_type or location",
                "providers": []
            }
            trace = make_trace(
                step_name="discovery",
                agent_name=self.name,
                input_data={"intent": intent},
                output_data=dict(state["discovery"]),
                tool_called="find_nearby_providers",
                start_time=start_time,
                status="skipped",
                reasoning_summary="Missing service_type or location in intent, discovery skipped."
            )
            state["discovery"]["trace"] = trace
            if "agent_trace" in state:
                state["agent_trace"].append(trace)
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

        trace = make_trace(
            step_name="discovery",
            agent_name=self.name,
            input_data={"location": location, "service_type": service_type},
            output_data=dict(state["discovery"]),
            tool_called="find_nearby_providers",
            start_time=start_time,
            status="fallback" if discovery_result.get("fallback_used") else "success",
            reasoning_summary=f"Found {len(providers)} providers nearby using Google Maps API mock."
        )
        state["discovery"]["trace"] = trace
        if "agent_trace" in state:
            state["agent_trace"].append(trace)

        return state