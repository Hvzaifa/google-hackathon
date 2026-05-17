"""
Trace logging utility matching team contract format.
Required fields per team doc [2]: step, agent_name, input, output, tool_called, duration_ms, status, reasoning_summary
"""

import time
from typing import Any, Dict

def make_trace(
    step_name: str,
    agent_name: str = "UnknownAgent",
    input_data: Any = None,
    output_data: Any = None,
    tool_called: str = "unknown_tool",
    start_time: float = None,
    status: str = "success",
    reasoning_summary: str = "Execution completed",
    errors: list[str] = None
) -> Dict[str, Any]:
    """
    Create a trace entry matching the team contract format.
    """
    import os
    import json

    trace_entry = {
        "step": step_name,
        "agent_name": agent_name,
        "input": input_data,
        "output": output_data,
        "tool_called": tool_called,
        "duration_ms": int((time.time() - start_time) * 1000) if start_time is not None else 0,
        "status": status,
        "reasoning_summary": reasoning_summary,
        "errors": errors or []
    }

    # Debug file logging if DEBUG mode is enabled
    if os.getenv("DEBUG", "false").lower() == "true":
        try:
            # Store in backend/debug_traces.log
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            log_file = os.path.join(backend_dir, "debug_traces.log")
            log_item = {
                "type": "agent_trace",
                "timestamp": time.time(),
                "data": trace_entry
            }
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_item) + "\n")
        except Exception:
            pass

    return trace_entry