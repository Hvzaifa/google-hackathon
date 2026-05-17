"""
Trace logging utility matching team contract format.
Required fields per team doc [2]: step, agent_name, input, output, tool_called, duration_ms, status, reasoning_summary
"""

import time
from typing import Any, Dict

def make_trace(
    step_name: str,
    agent_name: str,
    input_data: Any,
    output_data: Any,
    tool_called: str,
    start_time: float,
    status: str,
    reasoning_summary: str
) -> Dict[str, Any]:
    """
    Create a trace entry matching the team contract format.
    
    Args:
        step_name: One of intent, discovery, matching, pricing, booking, quality, dispute
        agent_name: Name of the agent that performed the step
        input_data: Input to the agent/step
        output_data: Output from the agent/step
        tool_called: Tool/API used
        start_time: time.time() from before execution
        status: success, error, fallback, clarification_needed
        reasoning_summary: Concise decision rationale (not raw CoT)
    """
    return {
        "step": step_name,
        "agent_name": agent_name,
        "input": input_data,
        "output": output_data,
        "tool_called": tool_called,
        "duration_ms": int((time.time() - start_time) * 1000),
        "status": status,
        "reasoning_summary": reasoning_summary,
    }