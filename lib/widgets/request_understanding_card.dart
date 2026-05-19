import 'package:flutter/material.dart';
import '../models/request_understanding.dart';
import '../themepage.dart';

class RequestUnderstandingCard extends StatelessWidget {
  final RequestUnderstanding data;
  const RequestUnderstandingCard({super.key, required this.data});

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
                child: const Icon(Icons.psychology, color: Colors.white, size: 18),
              ),
              const SizedBox(width: 10),
              const Text(
                'Request Understanding',
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: AppTheme.kPurple900,
                ),
              ),
              const Spacer(),
              if (data.confidence != null)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: data.confidence! >= 0.8
                        ? Colors.green.withValues(alpha: 0.1)
                        : Colors.orange.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    '${(data.confidence! * 100).toInt()}%',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: data.confidence! >= 0.8 ? Colors.green[700] : Colors.orange[700],
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 14),
          _row('Service', data.serviceType),
          _row('Issue', data.issueDescription),
          _row('Location', data.location),
          _row('When', data.datetimePreference),
          _row('Urgency', data.urgency),
          _row('Language', data.languageDetected),
          if (data.clarificationQuestion != null) ...[
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.amber.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.amber.withValues(alpha: 0.3)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.help_outline, size: 16, color: Colors.amber),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      data.clarificationQuestion!,
                      style: const TextStyle(fontSize: 12, color: AppTheme.kPurple900),
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

  Widget _row(String label, String? value) {
    if (value == null || value.isEmpty) return const SizedBox.shrink();
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
                color: AppTheme.kPurple300,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(fontSize: 13, color: AppTheme.kPurple900),
            ),
          ),
        ],
      ),
    );
  }
}
