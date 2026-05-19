import 'package:flutter/material.dart';
import '../models/provider.dart';
import '../themepage.dart';

class TopMatchesList extends StatelessWidget {
  final List<TopMatch> matches;
  const TopMatchesList({super.key, required this.matches});

  @override
  Widget build(BuildContext context) {
    if (matches.isEmpty) return const SizedBox.shrink();

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
                child: const Icon(Icons.leaderboard, color: Colors.white, size: 18),
              ),
              const SizedBox(width: 10),
              const Text(
                'Top Matches',
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: AppTheme.kPurple900,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ...matches.asMap().entries.map((entry) {
            final idx = entry.key;
            final match = entry.value;
            return _MatchTile(match: match, rank: idx + 1);
          }),
        ],
      ),
    );
  }
}

class _MatchTile extends StatefulWidget {
  final TopMatch match;
  final int rank;
  const _MatchTile({required this.match, required this.rank});

  @override
  State<_MatchTile> createState() => _MatchTileState();
}

class _MatchTileState extends State<_MatchTile> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final m = widget.match;
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: widget.rank == 1 ? AppTheme.kPurple50 : Colors.grey[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: widget.rank == 1 ? AppTheme.kPurple200 : Colors.grey[200]!,
        ),
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
                  CircleAvatar(
                    radius: 14,
                    backgroundColor: widget.rank == 1
                        ? AppTheme.kPurple400
                        : AppTheme.kPurple200,
                    child: Text(
                      '#${widget.rank}',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                        color: widget.rank == 1 ? Colors.white : AppTheme.kPurple900,
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          m.name ?? 'Unknown',
                          style: const TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: AppTheme.kPurple900,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Row(
                          children: [
                            if (m.rating != null) ...[
                              const Icon(Icons.star, size: 12, color: Colors.amber),
                              Text(' ${m.rating!.toStringAsFixed(1)}',
                                  style: const TextStyle(fontSize: 11)),
                              const SizedBox(width: 8),
                            ],
                            if (m.distanceKm != null)
                              Text('${m.distanceKm!.toStringAsFixed(1)} km',
                                  style: TextStyle(
                                      fontSize: 11, color: Colors.grey[600])),
                          ],
                        ),
                      ],
                    ),
                  ),
                  if (m.matchingScore != null)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: AppTheme.kPurple400.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        '${(m.matchingScore! * 100).toInt()}%',
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: AppTheme.kPurple700,
                        ),
                      ),
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
          if (_expanded && m.matchingScores != null)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Divider(height: 1),
                  const SizedBox(height: 8),
                  const Text(
                    'Why this match?',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: AppTheme.kPurple700,
                    ),
                  ),
                  const SizedBox(height: 6),
                  _scoreBar('Distance', m.matchingScores!.distanceScore),
                  _scoreBar('Rating', m.matchingScores!.ratingScore),
                  _scoreBar('On-time', m.matchingScores!.onTimeScore),
                  _scoreBar('Budget', m.matchingScores!.budgetScore),
                  _scoreBar('Reputation', m.matchingScores!.reputationScore),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _scoreBar(String label, double? value) {
    if (value == null) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          SizedBox(
            width: 70,
            child: Text(label,
                style: TextStyle(fontSize: 11, color: Colors.grey[600])),
          ),
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: value,
                minHeight: 6,
                backgroundColor: Colors.grey[200],
                valueColor:
                    const AlwaysStoppedAnimation<Color>(AppTheme.kPurple400),
              ),
            ),
          ),
          const SizedBox(width: 8),
          Text('${(value * 100).toInt()}%',
              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}
