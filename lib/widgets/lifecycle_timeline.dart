import 'package:flutter/material.dart';
import '../models/lifecycle_event.dart';
import '../themepage.dart';

class LifecycleTimeline extends StatelessWidget {
  final Lifecycle lifecycle;
  const LifecycleTimeline({super.key, required this.lifecycle});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.kPurple100),
        boxShadow: [
          BoxShadow(
            color: AppTheme.kPurple100.withValues(alpha: 0.5),
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
                  gradient: const LinearGradient(
                    colors: [AppTheme.kPurple400, AppTheme.kPurple700],
                  ),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.timeline, color: Colors.white, size: 18),
              ),
              const SizedBox(width: 10),
              const Text(
                'Lifecycle',
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: AppTheme.kPurple900,
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
                          color: isLast ? Colors.green : AppTheme.kPurple400,
                        ),
                      ),
                      if (!isLast)
                        Container(width: 2, height: 30, color: AppTheme.kPurple200),
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
                            style: const TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.w600,
                              color: AppTheme.kPurple900,
                            ),
                          ),
                          if (evt.details != null)
                            Text(evt.details!,
                                style: TextStyle(fontSize: 11, color: Colors.grey[600])),
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
              style: const TextStyle(fontSize: 12, color: AppTheme.kPurple900, height: 1.4),
            ),
          ],
        ],
      ),
    );
  }
}
