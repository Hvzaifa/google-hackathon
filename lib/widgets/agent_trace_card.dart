import 'package:flutter/material.dart';
import '../models/agent_trace.dart';
import '../themepage.dart';

class AgentTraceCard extends StatefulWidget {
  final AgentTrace trace;
  const AgentTraceCard({super.key, required this.trace});

  @override
  State<AgentTraceCard> createState() => _AgentTraceCardState();
}

class _AgentTraceCardState extends State<AgentTraceCard> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final t = widget.trace;
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.kPurple100),
      ),
      child: Column(
        children: [
          InkWell(
            onTap: () => setState(() => _expanded = !_expanded),
            borderRadius: BorderRadius.circular(12),
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Row(
                children: [
                  Container(
                    width: 32,
                    height: 32,
                    decoration: BoxDecoration(
                      color: AppTheme.kPurple50,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(_stepIcon(t.step), size: 16, color: AppTheme.kPurple400),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          t.step ?? 'Step',
                          style: const TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: AppTheme.kPurple900,
                          ),
                        ),
                        if (t.toolCalled != null)
                          Text(t.toolCalled!,
                              style: TextStyle(fontSize: 11, color: Colors.grey[500])),
                      ],
                    ),
                  ),
                  if (t.durationMs != null)
                    Text(
                      '${t.durationMs}ms',
                      style: TextStyle(fontSize: 11, color: Colors.grey[500]),
                    ),
                  const SizedBox(width: 6),
                  Icon(
                    _expanded ? Icons.expand_less : Icons.expand_more,
                    color: AppTheme.kPurple300,
                    size: 20,
                  ),
                ],
              ),
            ),
          ),
          if (_expanded) ...[
            const Divider(height: 1),
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (t.summary != null) ...[
                    const Text('Summary',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppTheme.kPurple700)),
                    const SizedBox(height: 4),
                    Text(t.summary!, style: const TextStyle(fontSize: 12, color: AppTheme.kPurple900)),
                    const SizedBox(height: 8),
                  ],
                  if (t.input != null) ...[
                    const Text('Input',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppTheme.kPurple700)),
                    const SizedBox(height: 4),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.grey[50],
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text('${t.input}',
                          style: TextStyle(fontSize: 11, color: Colors.grey[700], fontFamily: 'monospace')),
                    ),
                    const SizedBox(height: 8),
                  ],
                  if (t.output != null) ...[
                    const Text('Output',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppTheme.kPurple700)),
                    const SizedBox(height: 4),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.grey[50],
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text('${t.output}',
                          style: TextStyle(fontSize: 11, color: Colors.grey[700], fontFamily: 'monospace')),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  IconData _stepIcon(String? step) {
    switch (step?.toLowerCase()) {
      case 'intent':
        return Icons.psychology;
      case 'discovery':
        return Icons.search;
      case 'matching':
        return Icons.leaderboard;
      case 'pricing':
        return Icons.payments;
      case 'booking':
        return Icons.calendar_month;
      case 'lifecycle':
        return Icons.timeline;
      default:
        return Icons.bolt;
    }
  }
}
