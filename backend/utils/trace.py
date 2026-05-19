import time
from typing import Any, Dict

def make_trace(
    step_name: str,
    input_data: Any,
    output_data: Any,
    tool_called: str | None,
    start_time: float,
    trace_type: str = "reasoning",
) -> Dict[str, Any]:
    return {
        "step": step_name,
        "input": input_data,
        "output": output_data,
        "tool_called": tool_called,
        "duration_ms": max(1, int((time.time() - start_time) * 1000)),
        "trace_type": trace_type,
        "antigravity_trace_note": (
            "Executed as part of the Google ADK/Antigravity agent workflow"
        ),
    }