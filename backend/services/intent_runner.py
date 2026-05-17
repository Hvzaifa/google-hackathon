from dotenv import load_dotenv

load_dotenv()


from agents.intent_agent import IntentAgent

def run_intent_agent(message: str, use_gemini: bool = False) -> dict:
    agent = IntentAgent()
    state = {
        "user_message": message,
        "use_gemini": use_gemini,
        "agent_trace": []
    }
    state = agent.run(state)
    return {
        "status": state["intent_status"],
        "intent": state["intent"],
        "agent_trace": state["agent_trace"]
    }