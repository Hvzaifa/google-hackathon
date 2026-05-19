def generate_provider_optimization_note(
    selected_provider: dict,
    scheduling: dict,
) -> dict:
    status = scheduling.get("scheduling_status")

    if status == "conflict_detected":
        note = (
            "Provider has overlapping demand. Alternate slots were suggested "
            "to avoid double booking and improve workload balance."
        )
        recommendation = "Use alternate slot or select next best provider."
    else:
        note = (
            "Provider workload appears available for the requested slot. "
            "Job assignment supports fair utilization."
        )
        recommendation = "Proceed with booking."

    return {
        "status": "provider_optimization_generated",
        "provider_name": selected_provider.get("name"),
        "workload_status": status,
        "optimization_note": note,
        "recommendation": recommendation
    }