import 'package:flutter/material.dart';
import '../models/lifecycle_event.dart';

class LifecycleTimeline extends StatelessWidget {
  final Lifecycle lifecycle;
  const LifecycleTimeline({super.key, required this.lifecycle});

  static const List<String> _stages = [
    'Technician Assigned',
    'On The Way',
    'Arrived',
    'Service In Progress',
    'Completed',
    'Feedback Requested',
  ];

  Map<int, LifecycleEvent> _mapEventsToStages(List<LifecycleEvent>? events) {
    final map = <int, LifecycleEvent>{};
    if (events == null) return map;

    for (var evt in events) {
      final type = evt.event?.toLowerCase() ?? '';
      if (type.contains('technician_assigned') || type.contains('assigned')) map[0] = evt;
      else if (type.contains('on_the_way') || type.contains('way')) map[1] = evt;
      else if (type.contains('arrived')) map[2] = evt;
      else if (type.contains('service_started') || type.contains('in_progress')) map[3] = evt;
      else if (type.contains('service_completed') || type.contains('completed')) map[4] = evt;
      else if (type.contains('feedback_requested') || type.contains('feedback')) map[5] = evt;
    }
    return map;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    final stageMap = _mapEventsToStages(lifecycle.events);
    int maxIndex = -1;
    if (stageMap.isNotEmpty) {
      maxIndex = stageMap.keys.reduce((a, b) => a > b ? a : b);
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: theme.dividerColor.withValues(alpha: 0.1)),
        boxShadow: [
          BoxShadow(
            color: theme.shadowColor.withValues(alpha: isDark ? 0.2 : 0.05),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      theme.colorScheme.primary,
                      theme.colorScheme.primary.withValues(alpha: 0.8),
                    ],
                  ),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.timeline, color: Colors.white, size: 18),
              ),
              const SizedBox(width: 10),
              Text(
                'Lifecycle',
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: theme.colorScheme.onSurface,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ..._stages.asMap().entries.map((entry) {
            final idx = entry.key;
            final stageName = entry.value;
            final isLast = idx == _stages.length - 1;

            final isCompleted = idx < maxIndex;
            final isActive = idx == maxIndex;
            final isFuture = idx > maxIndex;

            Color dotColor;
            if (isCompleted) {
              dotColor = isDark ? Colors.green[400]! : Colors.green;
            } else if (isActive) {
              dotColor = theme.colorScheme.primary;
            } else {
              dotColor = theme.dividerColor.withValues(alpha: 0.3);
            }

            Color lineColor;
            if (idx < maxIndex) {
              lineColor = isDark ? Colors.green[400]!.withValues(alpha: 0.5) : Colors.green.withValues(alpha: 0.5);
            } else {
              lineColor = theme.dividerColor.withValues(alpha: 0.1);
            }

            Color textColor = isFuture ? theme.colorScheme.onSurface.withValues(alpha: 0.4) : theme.colorScheme.onSurface;
            
            String details = stageMap[idx]?.details ?? '';

            return Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Column(
                  children: [
                    Container(
                      width: isActive ? 14 : 10,
                      height: isActive ? 14 : 10,
                      margin: EdgeInsets.only(left: isActive ? 0 : 2, right: isActive ? 0 : 2),
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: dotColor,
                        border: isActive ? Border.all(color: theme.colorScheme.primary.withValues(alpha: 0.3), width: 3) : null,
                      ),
                    ),
                    if (!isLast)
                      Container(
                        width: 2,
                        height: details.isNotEmpty ? 40 : 24,
                        color: lineColor,
                      ),
                  ],
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          stageName,
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: isActive ? FontWeight.w700 : FontWeight.w600,
                            color: textColor,
                          ),
                        ),
                        if (details.isNotEmpty) ...[
                          const SizedBox(height: 2),
                          Text(
                            details,
                            style: TextStyle(
                              fontSize: 11,
                              color: theme.colorScheme.onSurface.withValues(alpha: 0.6),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              ],
            );
          }),
          if (lifecycle.summary != null) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: theme.colorScheme.primary.withValues(alpha: 0.05),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: theme.colorScheme.primary.withValues(alpha: 0.1)),
              ),
              child: Text(
                lifecycle.summary!,
                style: TextStyle(fontSize: 12, color: theme.colorScheme.onSurface, height: 1.4),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
