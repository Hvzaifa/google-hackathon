import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../themepage.dart';

class RescheduleScreen extends StatefulWidget {
  const RescheduleScreen({super.key});

  @override
  State<RescheduleScreen> createState() => _RescheduleScreenState();
}

class _RescheduleScreenState extends State<RescheduleScreen> {
  DateTime? _selectedDate;
  String? _selectedSlot;

  final List<String> _slots = [
    '09:00 - 11:00',
    '11:00 - 13:00',
    '14:00 - 16:00',
    '16:00 - 18:00',
    '18:00 - 20:00',
  ];

  @override
  Widget build(BuildContext context) {
    final canConfirm = _selectedDate != null && _selectedSlot != null;
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      resizeToAvoidBottomInset: true,
      body: Stack(
        children: [
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: Container(
              height: 260,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: isDark
                      ? [
                          theme.colorScheme.primary.withValues(alpha: 0.15),
                          theme.scaffoldBackgroundColor,
                        ]
                      : [const Color(0xFFF3F0FF), Colors.white],
                ),
              ),
            ),
          ),
          SafeArea(
            child: Column(
              children: [
                // Fixed header
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 16, vertical: 12),
                  decoration: BoxDecoration(
                    color: theme.scaffoldBackgroundColor.withValues(alpha: 0.8),
                    border: Border(
                      bottom: BorderSide(color: theme.dividerColor.withValues(alpha: 0.1)),
                    ),
                  ),
                  child: Row(
                    children: [
                      GestureDetector(
                        onTap: () => Navigator.pop(context),
                        child: Container(
                          width: 38,
                          height: 38,
                          decoration: BoxDecoration(
                            color: theme.colorScheme.surface,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: theme.dividerColor.withValues(alpha: 0.2)),
                          ),
                          child: Icon(
                            Icons.arrow_back_ios_new_rounded,
                            color: theme.colorScheme.primary,
                            size: 16,
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Text(
                        'Reschedule',
                        style: GoogleFonts.dmSans(
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                          color: theme.colorScheme.onSurface,
                        ),
                      ),
                    ],
                  ),
                ),
                // Scrollable body — prevents overflow
                Expanded(
                  child: LayoutBuilder(
                    builder: (context, constraints) {
                      return SingleChildScrollView(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 24, vertical: 16),
                        child: ConstrainedBox(
                          constraints: BoxConstraints(
                              minHeight: constraints.maxHeight),
                          child: IntrinsicHeight(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const SizedBox(height: 16),
                                Text(
                                  'Pick a new\ndate & time',
                                  style: GoogleFonts.dmSans(
                                    fontSize: 26,
                                    fontWeight: FontWeight.w700,
                                    color: theme.colorScheme.onSurface,
                                    height: 1.3,
                                  ),
                                ),
                                const SizedBox(height: 6),
                                Text(
                                  'Choose a convenient slot for your service.',
                                  style: GoogleFonts.dmSans(
                                    fontSize: 13,
                                    color: theme.colorScheme.onSurface.withValues(alpha: 0.7),
                                  ),
                                ),
                                const SizedBox(height: 24),

                                // Date picker card
                                GestureDetector(
                                  onTap: () async {
                                    final date = await showDatePicker(
                                      context: context,
                                      initialDate: DateTime.now()
                                          .add(const Duration(days: 1)),
                                      firstDate: DateTime.now(),
                                      lastDate: DateTime.now()
                                          .add(const Duration(days: 30)),
                                    );
                                    if (date != null) {
                                      setState(() => _selectedDate = date);
                                    }
                                  },
                                  child: Container(
                                    width: double.infinity,
                                    padding: const EdgeInsets.all(16),
                                    decoration: BoxDecoration(
                                      color: _selectedDate != null
                                          ? theme.colorScheme.primary.withValues(alpha: 0.08)
                                          : theme.colorScheme.surface,
                                      borderRadius:
                                          BorderRadius.circular(14),
                                      border: Border.all(
                                        color: _selectedDate != null
                                            ? theme.colorScheme.primary
                                            : theme.dividerColor.withValues(alpha: 0.2),
                                      ),
                                      boxShadow: [
                                        BoxShadow(
                                          color: theme.shadowColor.withValues(alpha: 0.1),
                                          blurRadius: 8,
                                          offset: const Offset(0, 2),
                                        ),
                                      ],
                                    ),
                                    child: Row(
                                      children: [
                                        Container(
                                          width: 36,
                                          height: 36,
                                          decoration: BoxDecoration(
                                            color: _selectedDate != null
                                                ? theme.colorScheme.primary
                                                : theme.colorScheme.surfaceContainerHighest,
                                            borderRadius:
                                                BorderRadius.circular(10),
                                          ),
                                          child: Icon(
                                            Icons.calendar_today_rounded,
                                            size: 16,
                                            color: _selectedDate != null
                                                ? theme.colorScheme.onPrimary
                                                : theme.colorScheme.primary,
                                          ),
                                        ),
                                        const SizedBox(width: 12),
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment:
                                                CrossAxisAlignment.start,
                                            children: [
                                              Text(
                                                'Date',
                                                style: GoogleFonts.dmSans(
                                                  fontSize: 11,
                                                  color: theme.colorScheme.onSurface.withValues(alpha: 0.6),
                                                  fontWeight: FontWeight.w500,
                                                ),
                                              ),
                                              const SizedBox(height: 2),
                                              Text(
                                                _selectedDate != null
                                                    ? '${_selectedDate!.day}/${_selectedDate!.month}/${_selectedDate!.year}'
                                                    : 'Tap to select a date',
                                                style: GoogleFonts.dmSans(
                                                  fontSize: 14,
                                                  fontWeight: FontWeight.w600,
                                                  color: _selectedDate != null
                                                      ? theme.colorScheme.onSurface
                                                      : theme.colorScheme.onSurface.withValues(alpha: 0.4),
                                                ),
                                              ),
                                            ],
                                          ),
                                        ),
                                        Icon(
                                          Icons.chevron_right_rounded,
                                          color: theme.colorScheme.onSurface.withValues(alpha: 0.4),
                                          size: 22,
                                        ),
                                      ],
                                    ),
                                  ),
                                ),

                                const SizedBox(height: 20),

                                // Time slot label
                                Text(
                                  'Available time slots',
                                  style: GoogleFonts.dmSans(
                                    fontSize: 14,
                                    fontWeight: FontWeight.w600,
                                    color: theme.colorScheme.onSurface,
                                  ),
                                ),
                                const SizedBox(height: 12),

                                // Time slots
                                Wrap(
                                  spacing: 10,
                                  runSpacing: 10,
                                  children: _slots.map((slot) {
                                    final selected =
                                        _selectedSlot == slot;
                                    return GestureDetector(
                                      onTap: () => setState(
                                          () => _selectedSlot = slot),
                                      child: AnimatedContainer(
                                        duration:
                                            const Duration(milliseconds: 200),
                                        padding:
                                            const EdgeInsets.symmetric(
                                                horizontal: 18,
                                                vertical: 12),
                                        decoration: BoxDecoration(
                                          color: selected
                                              ? theme.colorScheme.primary
                                              : theme.colorScheme.surface,
                                          borderRadius:
                                              BorderRadius.circular(12),
                                          border: Border.all(
                                            color: selected
                                                ? theme.colorScheme.primary
                                                : theme.dividerColor.withValues(alpha: 0.2),
                                          ),
                                          boxShadow: selected
                                              ? [
                                                  BoxShadow(
                                                    color: theme.colorScheme.primary.withValues(alpha: 0.3),
                                                    blurRadius: 8,
                                                    offset: const Offset(0, 2),
                                                  ),
                                                ]
                                              : null,
                                        ),
                                        child: Text(
                                          slot,
                                          style: GoogleFonts.dmSans(
                                            fontSize: 13,
                                            fontWeight: FontWeight.w500,
                                            color: selected
                                                ? theme.colorScheme.onPrimary
                                                : theme.colorScheme.onSurface,
                                          ),
                                        ),
                                      ),
                                    );
                                  }).toList(),
                                ),

                                const Spacer(),
                                const SizedBox(height: 24),

                                // Confirm button
                                SizedBox(
                                  width: double.infinity,
                                  child: GestureDetector(
                                    onTap: canConfirm
                                        ? () => Navigator.pop(context)
                                        : null,
                                    child: AnimatedContainer(
                                      duration:
                                          const Duration(milliseconds: 200),
                                      padding: const EdgeInsets.symmetric(
                                          vertical: 16),
                                      decoration: BoxDecoration(
                                        gradient: canConfirm
                                            ? LinearGradient(
                                                colors: [
                                                  theme.colorScheme.primary,
                                                  theme.colorScheme.primary.withValues(alpha: 0.8),
                                                ],
                                              )
                                            : null,
                                        color: canConfirm
                                            ? null
                                            : theme.disabledColor.withValues(alpha: 0.2),
                                        borderRadius:
                                            BorderRadius.circular(16),
                                        boxShadow: canConfirm
                                            ? [
                                                BoxShadow(
                                                  color: theme.colorScheme.primary.withValues(alpha: 0.4),
                                                  blurRadius: 12,
                                                  offset:
                                                      const Offset(0, 4),
                                                ),
                                              ]
                                            : null,
                                      ),
                                      child: Center(
                                        child: Text(
                                          'Confirm Reschedule',
                                          style: GoogleFonts.dmSans(
                                            fontSize: 16,
                                            fontWeight: FontWeight.w600,
                                            color: canConfirm
                                                ? theme.colorScheme.onPrimary
                                                : theme.disabledColor,
                                          ),
                                        ),
                                      ),
                                    ),
                                  ),
                                ),

                                const SizedBox(height: 16),
                              ],
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
