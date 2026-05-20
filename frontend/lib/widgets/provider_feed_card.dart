import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';

class ProviderFeedCard extends StatelessWidget {
  final List<Map<String, dynamic>> notifications;
  const ProviderFeedCard({super.key, required this.notifications});

  String _formatTimestamp(String? iso) {
    if (iso == null || iso.isEmpty) {
      return DateFormat('hh:mm a · dd MMM yyyy').format(DateTime.now());
    }
    try {
      final dt = DateTime.parse(iso);
      return DateFormat('hh:mm a · dd MMM yyyy').format(dt);
    } catch (_) {
      return iso;
    }
  }

  Widget _infoRow(BuildContext context, String label, String value) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 65,
            child: Text(
              '$label:',
              style: GoogleFonts.dmSans(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: theme.colorScheme.secondary,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: GoogleFonts.dmSans(
                fontSize: 12,
                color: theme.colorScheme.onSurface,
                height: 1.4,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _messageBlock(BuildContext context, String message) {
    final theme = Theme.of(context);
    String formattedMessage = message
        .replaceAll('. Location: ', '.\nLocation: ')
        .replaceAll('. Scheduled slot: ', '\nScheduled Slot: ')
        .replaceAll('. Estimated price: ', '\nEstimated Price: ')
        .replaceAll('. Booking ID: ', '\nBooking ID: ');

    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Message:',
            style: GoogleFonts.dmSans(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: theme.colorScheme.secondary,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            formattedMessage,
            style: GoogleFonts.dmSans(
              fontSize: 12,
              color: theme.colorScheme.onSurface,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }

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
            theme.colorScheme.secondary.withValues(alpha: isDark ? 0.15 : 0.06),
            theme.colorScheme.secondary.withValues(alpha: isDark ? 0.05 : 0.04),
          ],
        ),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: theme.colorScheme.secondary.withValues(alpha: isDark ? 0.4 : 0.20),
        ),
        boxShadow: [
          BoxShadow(
            color: theme.colorScheme.secondary.withValues(alpha: isDark ? 0.1 : 0.08),
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
              color: theme.colorScheme.secondary.withValues(alpha: isDark ? 0.1 : 0.05),
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
                        theme.colorScheme.secondary,
                        theme.colorScheme.secondary.withValues(alpha: 0.8),
                      ],
                    ),
                    borderRadius: BorderRadius.circular(11),
                    boxShadow: [
                      BoxShadow(
                        color: theme.colorScheme.secondary.withValues(alpha: 0.3),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: const Icon(
                    Icons.storefront_rounded,
                    color: Colors.white,
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Provider Activity Feed',
                        style: GoogleFonts.dmSans(
                          fontSize: 15,
                          fontWeight: FontWeight.w700,
                          color: theme.colorScheme.onSurface,
                        ),
                      ),
                      Text(
                        '${notifications.length} notification${notifications.length != 1 ? 's' : ''} sent',
                        style: GoogleFonts.dmSans(
                          fontSize: 11,
                          color: theme.colorScheme.onSurface.withValues(alpha: 0.6),
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 5,
                  ),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.secondary.withValues(alpha: 0.10),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: theme.colorScheme.secondary.withValues(alpha: 0.25),
                    ),
                  ),
                  child: Text(
                    'DEMO',
                    style: GoogleFonts.dmSans(
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                      color: theme.colorScheme.secondary,
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Notification cards
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
            child: Column(
              children: notifications.asMap().entries.map((entry) {
                final n = entry.value;
                final isLast = entry.key == notifications.length - 1;

                return Column(
                  children: [
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: isDark ? 0.3 : 0.5),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(
                          color: theme.dividerColor.withValues(alpha: 0.1),
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _infoRow(context, 'Title', n['title'] ?? 'Notification'),
                          const SizedBox(height: 4),
                          _infoRow(context, 'Channel', n['channel'] ?? 'unknown'),
                          const SizedBox(height: 4),
                          _messageBlock(context, n['message'] ?? ''),
                          const SizedBox(height: 10),
                          _infoRow(context, 'Status', n['status'] ?? 'simulated'),
                          const SizedBox(height: 4),
                          _infoRow(context, 'Time', _formatTimestamp(n['created_at'])),
                        ],
                      ),
                    ),
                    if (!isLast) const SizedBox(height: 10),
                  ],
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }
}
