import time
from typing import Any, Dict

def make_trace(
    step_name: str,
    input_data: Any,
    output_data: Any,
    tool_called: str | None,
    start_time: float,
) -> Dict[str, Any]:
    return {
        "step": step_name,
        "input": input_data,
        "output": output_data,
        "tool_called": tool_called,
        "duration_ms": int((time.time() - start_time) * 1000),
        "antigravity_trace_note": (
            "Executed as part of the Google ADK/Antigravity agent workflow"
        ),
    }