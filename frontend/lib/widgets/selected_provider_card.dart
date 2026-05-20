import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/provider.dart';

class SelectedProviderCard extends StatelessWidget {
  final SelectedProvider provider;
  const SelectedProviderCard({super.key, required this.provider});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            theme.colorScheme.primary.withValues(alpha: isDark ? 0.15 : 0.08),
            theme.colorScheme.surface,
          ],
        ),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: theme.colorScheme.primary.withValues(alpha: isDark ? 0.3 : 0.15)),
        boxShadow: [
          BoxShadow(
            color: theme.colorScheme.primary.withValues(alpha: isDark ? 0.15 : 0.1),
            blurRadius: 16,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: theme.colorScheme.primary.withValues(alpha: isDark ? 0.1 : 0.04),
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(18),
              ),
            ),
            child: Row(
              children: [
                Container(
                  width: 38,
                  height: 38,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        theme.colorScheme.primary,
                        theme.colorScheme.primary.withValues(alpha: 0.8),
                      ],
                    ),
                    borderRadius: BorderRadius.circular(11),
                    boxShadow: [
                      BoxShadow(
                        color: theme.colorScheme.primary.withValues(alpha: 0.3),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: const Icon(Icons.verified_rounded,
                      color: Colors.white, size: 20),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Selected Provider',
                        style: GoogleFonts.dmSans(
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                          color: theme.colorScheme.primary,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        provider.name ?? 'Unknown',
                        style: GoogleFonts.dmSans(
                          fontSize: 17,
                          fontWeight: FontWeight.w700,
                          color: theme.colorScheme.onSurface,
                        ),
                        overflow: TextOverflow.ellipsis,
                        maxLines: 2,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Metrics — using Wrap to prevent overflow on small screens
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 10, 16, 16),
            child: Wrap(
              spacing: 16,
              runSpacing: 10,
              children: [
                if (provider.rating != null)
                  _metricChip(
                    Icons.star_rounded,
                    provider.rating!.toStringAsFixed(1),
                    Colors.amber,
                  ),
                if (provider.distanceKm != null)
                  _metricChip(
                    Icons.location_on_rounded,
                    '${provider.distanceKm!.toStringAsFixed(1)} km',
                    theme.colorScheme.primary,
                  ),
                if (provider.matchingScore != null)
                  _metricChip(
                    Icons.speed_rounded,
                    '${(provider.matchingScore! * 100).toInt()}% match',
                    const Color(0xFF16A34A),
                  ),
                if (provider.source != null)
                  _metricChip(
                    provider.source == 'google_maps'
                        ? Icons.map_rounded
                        : Icons.data_object_rounded,
                    provider.source == 'google_maps'
                        ? 'Google Maps'
                        : 'Fallback',
                    Colors.blue,
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _metricChip(IconData icon, String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: color.withValues(alpha: 0.15)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: color),
          const SizedBox(width: 5),
          Text(
            text,
            style: GoogleFonts.dmSans(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: color.withValues(alpha: 0.9),
            ),
          ),
        ],
      ),
    );
  }
}
