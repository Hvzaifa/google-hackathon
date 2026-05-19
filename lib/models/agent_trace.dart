class AgentTrace {
  final String? step;
  final String? toolCalled;
  final num? durationMs;
  final String? summary;
  final dynamic input;
  final dynamic output;

  const AgentTrace({
    this.step,
    this.toolCalled,
    this.durationMs,
    this.summary,
    this.input,
    this.output,
  });

  factory AgentTrace.fromJson(Map<String, dynamic> json) {
    return AgentTrace(
      step: json['step'],
      toolCalled: json['tool_called'],
      durationMs: json['duration_ms'],
      summary: json['summary'],
      input: json['input'],
      output: json['output'],
    );
  }
}
