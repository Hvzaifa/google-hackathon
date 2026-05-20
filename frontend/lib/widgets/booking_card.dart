import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import '../models/booking.dart';
import '../screens/reschedule_screen.dart';

class BookingCard extends StatelessWidget {
  final Booking booking;
  const BookingCard({super.key, required this.booking});

  String _formatTimeSlot(String? iso) {
    if (iso == null || iso.isEmpty) return '—';
    try {
      final dt = DateTime.parse(iso).toLocal();
      return DateFormat('hh:mm a').format(dt);
    } catch (_) {
      return iso;
    }
  }

  String _formatDate(String? iso) {
    if (iso == null || iso.isEmpty) {
      return DateFormat('dd MMM yyyy').format(DateTime.now());
    }
    try {
      final dt = DateTime.parse(iso).toLocal();
      return DateFormat('dd MMM yyyy').format(dt);
    } catch (_) {
      return iso;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    final accentColor = _cardAccentColor(booking.status);

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            accentColor.withValues(alpha: isDark ? 0.15 : 0.06),
            theme.colorScheme.primary.withValues(alpha: isDark ? 0.05 : 0.05),
          ],
        ),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: accentColor.withValues(alpha: isDark ? 0.4 : 0.25)),
        boxShadow: [
          BoxShadow(
            color: accentColor.withValues(alpha: isDark ? 0.1 : 0.08),
            blurRadius: 16,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header section
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: _headerBgColor(booking.status, isDark),
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
                      colors: _headerGradient(booking.status),
                    ),
                    borderRadius: BorderRadius.circular(11),
                    boxShadow: [
                      BoxShadow(
                        color: _headerGradient(booking.status).first.withValues(alpha: 0.3),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Icon(
                    _headerIcon(booking.status),
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
                        _headerTitle(booking.status),
                        style: GoogleFonts.dmSans(
                          fontSize: 15,
                          fontWeight: FontWeight.w700,
                          color: theme.colorScheme.onSurface,
                        ),
                      ),
                      if (booking.bookingId != null)
                        Text(
                          'ID: ${booking.bookingId}',
                          style: GoogleFonts.dmSans(
                            fontSize: 11,
                            color: theme.colorScheme.onSurface.withValues(alpha: 0.6),
                          ),
                          overflow: TextOverflow.ellipsis,
                          maxLines: 1,
                        ),
                    ],
                  ),
                ),
                if (booking.status != null)
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 5,
                    ),
                    decoration: BoxDecoration(
                      color: _statusColor(
                        booking.status!,
                        isDark,
                      ).withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: _statusColor(
                          booking.status!,
                          isDark,
                        ).withValues(alpha: 0.3),
                      ),
                    ),
                    child: Text(
                      booking.status!,
                      style: GoogleFonts.dmSans(
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        color: _statusColor(booking.status!, isDark),
                      ),
                    ),
                  ),
              ],
            ),
          ),

          // Details section
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ETA chip
                if (booking.etaMinutes != null)
                  Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 8,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.blue.withValues(alpha: isDark ? 0.15 : 0.08),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(
                        color: Colors.blue.withValues(alpha: isDark ? 0.3 : 0.15),
                      ),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.access_time_filled_rounded,
                          size: 14,
                          color: isDark ? Colors.blue[300] : Colors.blue[600],
                        ),
                        const SizedBox(width: 6),
                        Text(
                          'ETA: ${booking.etaMinutes} minutes',
                          style: GoogleFonts.dmSans(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: isDark ? Colors.blue[300] : Colors.blue[700],
                          ),
                        ),
                      ],
                    ),
                  ),

                // Summary text
                if (booking.summary != null) ...[
                  Text(
                    booking.summary!,
                    style: GoogleFonts.dmSans(
                      fontSize: 13,
                      color: theme.colorScheme.onSurface,
                      height: 1.5,
                    ),
                    softWrap: true,
                  ),
                  const SizedBox(height: 12),
                ],

                // Scheduling info
                if (booking.scheduling != null) ...[
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.surface.withValues(alpha: isDark ? 0.3 : 0.7),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: theme.dividerColor.withValues(alpha: 0.1)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Schedule',
                          style: GoogleFonts.dmSans(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: theme.colorScheme.primary,
                          ),
                        ),
                        const SizedBox(height: 8),
                        _infoRow(
                          context,
                          Icons.access_time_rounded,
                          'Time Slot',
                          _formatTimeSlot(booking.scheduling!['assigned_slot']?.toString()),
                        ),
                        const SizedBox(height: 6),
                        _infoRow(
                          context,
                          Icons.calendar_today_rounded,
                          'Date',
                          _formatDate(booking.createdAt),
                        ),
                        if (booking.scheduling!['scheduling_status'] == 'conflict_detected' && booking.scheduling!['alternate_slots'] != null) ...[
                          const SizedBox(height: 16),
                          Text(
                            'Suggested Alternate Slots',
                            style: GoogleFonts.dmSans(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: theme.colorScheme.error,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Wrap(
                            spacing: 8,
                            runSpacing: 8,
                            children: (booking.scheduling!['alternate_slots'] as List).map((slot) {
                              return Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                decoration: BoxDecoration(
                                  color: theme.colorScheme.error.withValues(alpha: 0.1),
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(color: theme.colorScheme.error.withValues(alpha: 0.3)),
                                ),
                                child: Text(
                                  '${_formatDate(slot.toString())} at ${_formatTimeSlot(slot.toString())}',
                                  style: GoogleFonts.dmSans(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w500,
                                    color: theme.colorScheme.error,
                                  ),
                                ),
                              );
                            }).toList(),
                          ),
                          const SizedBox(height: 16),
                          SizedBox(
                            width: double.infinity,
                            child: ElevatedButton(
                              onPressed: () {
                                Navigator.push(context, MaterialPageRoute(builder: (context) => const RescheduleScreen()));
                              },
                              style: ElevatedButton.styleFrom(
                                backgroundColor: theme.colorScheme.error,
                                foregroundColor: theme.colorScheme.onError,
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                                padding: const EdgeInsets.symmetric(vertical: 12),
                                elevation: 0,
                              ),
                              child: Text('Reschedule Booking', style: GoogleFonts.dmSans(fontSize: 13, fontWeight: FontWeight.w600)),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Color _statusColor(String status, bool isDark) {
    switch (status.toLowerCase()) {
      case 'confirmed':
        return isDark ? Colors.green[400]! : const Color(0xFF16A34A);
      case 'pending':
      case 'pending_reschedule':
        return isDark ? Colors.orange[300]! : Colors.orange;
      case 'pending_sync':
        return isDark ? Colors.amber[300]! : Colors.amber[700]!;
      case 'cancelled':
        return isDark ? Colors.red[300]! : Colors.red;
      default:
        return isDark ? Colors.purple[300]! : Colors.purple;
    }
  }

  Color _cardAccentColor(String? status) {
    switch (status?.toLowerCase()) {
      case 'confirmed':
        return Colors.green;
      case 'pending_reschedule':
        return Colors.orange;
      case 'pending_sync':
        return Colors.amber;
      default:
        return Colors.green;
    }
  }

  Color _headerBgColor(String? status, bool isDark) {
    final accent = _cardAccentColor(status);
    return accent.withValues(alpha: isDark ? 0.1 : 0.05);
  }

  List<Color> _headerGradient(String? status) {
    switch (status?.toLowerCase()) {
      case 'confirmed':
        return [const Color(0xFF16A34A), const Color(0xFF22C55E)];
      case 'pending_reschedule':
        return [Colors.orange[700]!, Colors.orange[400]!];
      case 'pending_sync':
        return [Colors.amber[700]!, Colors.amber[500]!];
      default:
        return [const Color(0xFF16A34A), const Color(0xFF22C55E)];
    }
  }

  IconData _headerIcon(String? status) {
    switch (status?.toLowerCase()) {
      case 'confirmed':
        return Icons.check_circle_rounded;
      case 'pending_reschedule':
        return Icons.schedule_rounded;
      case 'pending_sync':
        return Icons.cloud_off_rounded;
      default:
        return Icons.check_circle_rounded;
    }
  }

  String _headerTitle(String? status) {
    switch (status?.toLowerCase()) {
      case 'confirmed':
        return 'Booking Confirmed';
      case 'pending_reschedule':
        return 'Scheduling Conflict';
      case 'pending_sync':
        return 'Booking Pending — Local Fallback';
      default:
        return 'Booking';
    }
  }

  Widget _infoRow(BuildContext context, IconData icon, String label, String value) {
    final theme = Theme.of(context);
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 14, color: theme.colorScheme.onSurface.withValues(alpha: 0.6)),
        const SizedBox(width: 8),
        SizedBox(
          width: 70,
          child: Text(
            label,
            style: GoogleFonts.dmSans(
                fontSize: 12, color: theme.colorScheme.onSurface.withValues(alpha: 0.6)),
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: GoogleFonts.dmSans(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: theme.colorScheme.onSurface,
            ),
            softWrap: true,
            overflow: TextOverflow.visible,
          ),
        ),
      ],
    );
  }
}
