from services.matching_service import rank_providers


class MatchingAgent:
    name = "MatchingAgent"

    def run(self, state: dict) -> dict:

        providers = state.get("providers", [])
        intent = state.get("intent", {})

        ranking_result = rank_providers(
            providers=providers,
            intent=intent
        )

        state["matching"] = ranking_result

        if ranking_result.get("selected_provider"):
            state["selected_provider"] = ranking_result[
                "selected_provider"
            ]

        return state