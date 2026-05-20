import 'package:flutter/material.dart';
import '../models/request_understanding.dart';

class RequestUnderstandingCard extends StatelessWidget {
  final RequestUnderstanding data;
  const RequestUnderstandingCard({super.key, required this.data});

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
                child: const Icon(Icons.psychology, color: Colors.white, size: 18),
              ),
              const SizedBox(width: 10),
              Text(
                'Request Understanding',
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: theme.colorScheme.onSurface,
                ),
              ),
              const Spacer(),
              if (data.confidence != null)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: data.confidence! >= 0.8
                        ? Colors.green.withValues(alpha: isDark ? 0.2 : 0.1)
                        : Colors.orange.withValues(alpha: isDark ? 0.2 : 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    '${(data.confidence! * 100).toInt()}%',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: data.confidence! >= 0.8 
                          ? (isDark ? Colors.green[300] : Colors.green[700]) 
                          : (isDark ? Colors.orange[300] : Colors.orange[700]),
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 14),
          _row(context, 'Service', data.serviceType),
          _row(context, 'Issue', data.issueDescription),
          _row(context, 'Location', data.location),
          _row(context, 'When', data.datetimePreference),
          _row(context, 'Urgency', data.urgency),
          _row(context, 'Language', data.languageDetected),
          if (data.clarificationQuestion != null) ...[
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.amber.withValues(alpha: isDark ? 0.15 : 0.1),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.amber.withValues(alpha: isDark ? 0.4 : 0.3)),
              ),
              child: Row(
                children: [
                  Icon(Icons.help_outline, size: 16, color: isDark ? Colors.amber[300] : Colors.amber),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      data.clarificationQuestion!,
                      style: TextStyle(fontSize: 12, color: theme.colorScheme.onSurface),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _row(BuildContext context, String label, String? value) {
    if (value == null || value.isEmpty) return const SizedBox.shrink();
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              label,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: theme.colorScheme.onSurface.withValues(alpha: 0.6),
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: TextStyle(fontSize: 13, color: theme.colorScheme.onSurface),
            ),
          ),
        ],
      ),
    );
  }
}
