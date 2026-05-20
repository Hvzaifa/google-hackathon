import 'package:flutter/material.dart';
import '../models/provider.dart';

class TopMatchesList extends StatelessWidget {
  final List<TopMatch> matches;
  const TopMatchesList({super.key, required this.matches});

  @override
  Widget build(BuildContext context) {
    if (matches.isEmpty) return const SizedBox.shrink();

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
                child: const Icon(Icons.leaderboard, color: Colors.white, size: 18),
              ),
              const SizedBox(width: 10),
              Text(
                'Top Matches',
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: theme.colorScheme.onSurface,
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
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final isTop = widget.rank == 1;

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: isTop 
            ? theme.colorScheme.primary.withValues(alpha: isDark ? 0.15 : 0.05) 
            : theme.colorScheme.surfaceContainerHighest.withValues(alpha: isDark ? 0.3 : 0.5),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isTop 
              ? theme.colorScheme.primary.withValues(alpha: 0.3) 
              : theme.dividerColor.withValues(alpha: 0.1),
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
                    backgroundColor: isTop
                        ? theme.colorScheme.primary
                        : theme.colorScheme.primary.withValues(alpha: 0.3),
                    child: Text(
                      '#${widget.rank}',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                        color: isTop ? theme.colorScheme.onPrimary : theme.colorScheme.onSurface,
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
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: theme.colorScheme.onSurface,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Row(
                          children: [
                            if (m.rating != null) ...[
                              Icon(Icons.star, size: 12, color: Colors.amber[600]),
                              Text(' ${m.rating!.toStringAsFixed(1)}',
                                  style: TextStyle(fontSize: 11, color: theme.colorScheme.onSurface)),
                              const SizedBox(width: 8),
                            ],
                            if (m.distanceKm != null)
                              Text('${m.distanceKm!.toStringAsFixed(1)} km',
                                  style: TextStyle(
                                      fontSize: 11, color: theme.colorScheme.onSurface.withValues(alpha: 0.6))),
                          ],
                        ),
                      ],
                    ),
                  ),
                  if (m.matchingScore != null)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.primary.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        '${(m.matchingScore! * 100).toInt()}%',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: theme.colorScheme.primary,
                        ),
                      ),
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
          if (_expanded && m.matchingScores != null)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Divider(height: 1, color: theme.dividerColor.withValues(alpha: 0.1)),
                  const SizedBox(height: 8),
                  Text(
                    'Why this match?',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: theme.colorScheme.primary,
                    ),
                  ),
                  const SizedBox(height: 6),
                  _scoreBar(context, 'Distance', m.matchingScores!.distanceScore),
                  _scoreBar(context, 'Rating', m.matchingScores!.ratingScore),
                  _scoreBar(context, 'On-time', m.matchingScores!.onTimeScore),
                  _scoreBar(context, 'Budget', m.matchingScores!.budgetScore),
                  _scoreBar(context, 'Reputation', m.matchingScores!.reputationScore),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _scoreBar(BuildContext context, String label, double? value) {
    if (value == null) return const SizedBox.shrink();
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          SizedBox(
            width: 70,
            child: Text(label,
                style: TextStyle(fontSize: 11, color: theme.colorScheme.onSurface.withValues(alpha: 0.6))),
          ),
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: value,
                minHeight: 6,
                backgroundColor: theme.colorScheme.surfaceContainerHighest.withValues(alpha: isDark ? 0.2 : 1.0),
                valueColor:
                    AlwaysStoppedAnimation<Color>(theme.colorScheme.primary),
              ),
            ),
          ),
          const SizedBox(width: 8),
          Text('${(value * 100).toInt()}%',
              style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: theme.colorScheme.onSurface)),
        ],
      ),
    );
  }
}
