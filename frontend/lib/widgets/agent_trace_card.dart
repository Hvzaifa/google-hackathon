import 'package:flutter/material.dart';
import '../models/agent_trace.dart';

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
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: theme.dividerColor.withValues(alpha: 0.1)),
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
                      color: theme.colorScheme.primary.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(_stepIcon(t.step), size: 16, color: theme.colorScheme.primary),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          t.step ?? 'Step',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: theme.colorScheme.onSurface,
                          ),
                        ),
                        if (t.toolCalled != null)
                          Text(t.toolCalled!,
                              style: TextStyle(fontSize: 11, color: theme.colorScheme.onSurface.withValues(alpha: 0.6))),
                      ],
                    ),
                  ),
                  if (t.durationMs != null)
                    Text(
                      '${t.durationMs}ms',
                      style: TextStyle(fontSize: 11, color: theme.colorScheme.onSurface.withValues(alpha: 0.6)),
                    ),
                  const SizedBox(width: 6),
                  Icon(
                    _expanded ? Icons.expand_less : Icons.expand_more,
                    color: theme.colorScheme.onSurface.withValues(alpha: 0.5),
                    size: 20,
                  ),
                ],
              ),
            ),
          ),
          if (_expanded) ...[
            Divider(height: 1, color: theme.dividerColor.withValues(alpha: 0.1)),
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (t.summary != null) ...[
                    Text('Summary',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: theme.colorScheme.primary)),
                    const SizedBox(height: 4),
                    Text(t.summary!, style: TextStyle(fontSize: 12, color: theme.colorScheme.onSurface)),
                    const SizedBox(height: 8),
                  ],
                  if (t.input != null) ...[
                    Text('Input',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: theme.colorScheme.primary)),
                    const SizedBox(height: 4),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: isDark ? 0.3 : 0.5),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text('${t.input}',
                          style: TextStyle(fontSize: 11, color: theme.colorScheme.onSurface.withValues(alpha: 0.8), fontFamily: 'monospace')),
                    ),
                    const SizedBox(height: 8),
                  ],
                  if (t.output != null) ...[
                    Text('Output',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: theme.colorScheme.primary)),
                    const SizedBox(height: 4),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: isDark ? 0.3 : 0.5),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text('${t.output}',
                          style: TextStyle(fontSize: 11, color: theme.colorScheme.onSurface.withValues(alpha: 0.8), fontFamily: 'monospace')),
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
