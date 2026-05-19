import 'package:flutter/material.dart';
import '../themepage.dart';

class CompletionEvidenceCard extends StatelessWidget {
  final Map<String, dynamic> evidence;
  const CompletionEvidenceCard({super.key, required this.evidence});

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
                child: const Icon(Icons.fact_check, color: Colors.white, size: 18),
              ),
              const SizedBox(width: 10),
              const Text(
                'Completion Evidence',
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: AppTheme.kPurple900,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ...evidence.entries.map((e) => Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(
                      width: 100,
                      child: Text(e.key,
                          style: TextStyle(fontSize: 12, color: AppTheme.kPurple300)),
                    ),
                    Expanded(
                      child: Text('${e.value}',
                          style: const TextStyle(fontSize: 12, color: AppTheme.kPurple900)),
                    ),
                  ],
                ),
              )),
        ],
      ),
    );
  }
}
