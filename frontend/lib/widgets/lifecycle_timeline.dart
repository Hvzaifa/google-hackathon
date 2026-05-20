import 'package:flutter/material.dart';
import '../models/lifecycle_event.dart';

class LifecycleTimeline extends StatelessWidget {
  final Lifecycle lifecycle;
  const LifecycleTimeline({super.key, required this.lifecycle});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

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
          const SizedBox(height: 12),
          if (lifecycle.events != null)
            ...lifecycle.events!.asMap().entries.map((entry) {
              final idx = entry.key;
              final evt = entry.value;
              final isLast = idx == lifecycle.events!.length - 1;
              return Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Column(
                    children: [
                      Container(
                        width: 10,
                        height: 10,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: isLast ? (isDark ? Colors.green[400] : Colors.green) : theme.colorScheme.primary,
                        ),
                      ),
                      if (!isLast)
                        Container(width: 2, height: 30, color: theme.colorScheme.primary.withValues(alpha: 0.3)),
                    ],
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            evt.event ?? '',
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.w600,
                              color: theme.colorScheme.onSurface,
                            ),
                          ),
                          if (evt.details != null)
                            Text(evt.details!,
                                style: TextStyle(fontSize: 11, color: theme.colorScheme.onSurface.withValues(alpha: 0.6))),
                        ],
                      ),
                    ),
                  ),
                ],
              );
            }),
          if (lifecycle.summary != null) ...[
            const SizedBox(height: 6),
            Text(
              lifecycle.summary!,
              style: TextStyle(fontSize: 12, color: theme.colorScheme.onSurface, height: 1.4),
            ),
          ],
        ],
      ),
    );
  }
}
