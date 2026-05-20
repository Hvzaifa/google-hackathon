import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../providers/orchestration_provider.dart';
import '../themepage.dart';
import '../widgets/request_understanding_card.dart';
import '../widgets/selected_provider_card.dart';
import '../widgets/top_matches_list.dart';
import '../widgets/pricing_card.dart';
import '../widgets/booking_card.dart';
import '../widgets/lifecycle_timeline.dart';
import '../widgets/notifications_card.dart';
import '../widgets/completion_evidence_card.dart';
import '../widgets/provider_feed_card.dart';
import 'agent_trace_screen.dart';
import 'feedback_screen.dart';

class ResultsScreen extends ConsumerStatefulWidget {
  const ResultsScreen({super.key});

  @override
  ConsumerState<ResultsScreen> createState() => _ResultsScreenState();
}

class _ResultsScreenState extends ConsumerState<ResultsScreen>
    with TickerProviderStateMixin {
  bool _bookingConfirmed = false;
  List<Map<String, dynamic>>? _providerNotifications;
  late AnimationController _pulseController;
  late Animation<double> _pulseAnim;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);
    _pulseAnim = Tween<double>(begin: 0.85, end: 1.0).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  void _extractProviderNotifications() {
    final response = ref.read(orchestrationProvider).response;
    final embeddedNotifications =
        response?.booking?.notifications?['notifications'];
    if (embeddedNotifications is List) {
      _providerNotifications = embeddedNotifications
          .where((n) => n is Map && n['recipient_type'] == 'provider')
          .map((n) => Map<String, dynamic>.from(n as Map))
          .toList();
    }
  }

  void _showTopNotification() {
    late OverlayEntry overlayEntry;
    final animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 400),
    );
    final slideAnim = Tween<Offset>(
      begin: const Offset(1.0, 0.0),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(parent: animController, curve: Curves.easeOutCubic),
    );

    overlayEntry = OverlayEntry(
      builder: (ctx) {
        return Positioned(
          top: MediaQuery.of(ctx).padding.top + 12,
          left: 16,
          right: 16,
          child: SlideTransition(
            position: slideAnim,
            child: Material(
              color: Colors.transparent,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF7C3AED), Color(0xFF6D28D9)],
                  ),
                  borderRadius: BorderRadius.circular(14),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFF7C3AED).withValues(alpha: 0.35),
                      blurRadius: 16,
                      offset: const Offset(0, 6),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    Container(
                      width: 32,
                      height: 32,
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.2),
                        borderRadius: BorderRadius.circular(9),
                      ),
                      child: const Icon(Icons.send_rounded, color: Colors.white, size: 16),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Provider notification has been sent!',
                        style: GoogleFonts.dmSans(fontSize: 13, fontWeight: FontWeight.w600, color: Colors.white),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );

    Overlay.of(context).insert(overlayEntry);
    animController.forward();

    Future.delayed(const Duration(seconds: 3), () {
      animController.reverse().then((_) {
        overlayEntry.remove();
        animController.dispose();
      });
    });
  }

  Future<void> _handleConfirmBooking() async {
    final theme = Theme.of(context);
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: theme.colorScheme.surface,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text('Confirm Booking', style: GoogleFonts.dmSans(fontWeight: FontWeight.bold, color: theme.colorScheme.onSurface)),
        content: Text(
          'Are you sure you want to confirm this booking? The provider will be notified and a slot will be scheduled.',
          style: GoogleFonts.dmSans(color: theme.colorScheme.primary),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text('Cancel', style: GoogleFonts.dmSans(color: theme.colorScheme.onSurface.withValues(alpha: 0.6), fontWeight: FontWeight.w600)),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text('Yes, Book', style: GoogleFonts.dmSans(color: const Color(0xFF16A34A), fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    await ref.read(orchestrationProvider.notifier).confirmBooking();

    if (!mounted) return;

    final currentState = ref.read(orchestrationProvider);
    if (currentState.response?.booking != null && currentState.error == null) {
      setState(() => _bookingConfirmed = true);
      _extractProviderNotifications();
      _showTopNotification();
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final state = ref.watch(orchestrationProvider);
    final screenWidth = MediaQuery.of(context).size.width;
    final isTablet = screenWidth > 600;
    final horizontalPad = isTablet ? 32.0 : 16.0;

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      body: Stack(
        children: [
          Positioned(
            top: 0, left: 0, right: 0,
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
                Container(
                  padding: EdgeInsets.symmetric(horizontal: horizontalPad, vertical: 12),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.8),
                    border: Border(bottom: BorderSide(color: theme.dividerColor.withValues(alpha: 0.5))),
                  ),
                  child: Row(
                    children: [
                      GestureDetector(
                        onTap: () {
                          ref.read(orchestrationProvider.notifier).reset();
                          Navigator.pop(context);
                        },
                        child: Container(
                          width: 38, height: 38,
                          decoration: BoxDecoration(
                            color: theme.colorScheme.surface,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: theme.dividerColor),
                          ),
                          child: Icon(Icons.arrow_back_ios_new_rounded, color: theme.colorScheme.primary, size: 16),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Text('Results', style: GoogleFonts.poppins(fontSize: 25, fontWeight: FontWeight.bold, color: theme.colorScheme.onSurface)),
                      const Spacer(),
                      if (state.response != null)
                        GestureDetector(
                          onTap: () {
                            Navigator.push(context, MaterialPageRoute(
                              builder: (_) => AgentTraceScreen(traces: state.response!.agentTrace ?? []),
                            ));
                          },
                          child: Container(
                            width: 38, height: 38,
                            decoration: BoxDecoration(
                              color: theme.colorScheme.surface,
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(color: theme.dividerColor),
                            ),
                            child: Icon(Icons.timeline_rounded, color: theme.colorScheme.primary, size: 18),
                          ),
                        ),
                    ],
                  ),
                ),
                Expanded(child: _buildBody(context, state, horizontalPad)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBody(BuildContext context, OrchestrationState state, double hPad) {
    final theme = Theme.of(context);
    if (state.isLoading) return _buildLoadingState(context);
    if (state.error != null) return _buildErrorState(context, state.error!);

    final data = state.response;
    if (data == null) {
      return Center(child: Text('No data available', style: GoogleFonts.dmSans(fontSize: 14, color: theme.colorScheme.secondary)));
    }

    String dataSource = 'Unknown';
    bool isGoogleMapsData = false;
    String? fallbackReason;
    for (final trace in data.agentTrace ?? []) {
      if (trace.step?.toLowerCase() == 'discovery') {
        final tool = trace.toolCalled ?? '';
        if (tool.contains('google_maps')) {
          dataSource = 'Google Maps API (Live)';
          isGoogleMapsData = true;
        } else {
          dataSource = 'Mock / Fallback Data';
          if (trace.output is Map) {
            fallbackReason = (trace.output as Map)['fallback_reason']?.toString();
          }
        }
        break;
      }
    }

    return ListView(
      padding: EdgeInsets.symmetric(horizontal: hPad, vertical: 16),
      children: [
        if (data.status != null) _buildStatusBadge(context, data.status!),
        _buildDataSourceBadge(context, dataSource, isGoogleMapsData, fallbackReason),

        if (data.fallbackResponse != null)
          _buildFallbackCard(context, data.fallbackResponse!),

        if (data.paymentFallback != null)
          _buildPaymentFallbackCard(context, data.paymentFallback!),

        if (data.requestUnderstanding != null) ...[
          RequestUnderstandingCard(data: data.requestUnderstanding!),
          const SizedBox(height: 16),
        ],
        if (data.selectedProvider != null) ...[
          SelectedProviderCard(provider: data.selectedProvider!),
          const SizedBox(height: 16),
        ],
        if (data.topMatches != null && data.topMatches!.isNotEmpty) ...[
          TopMatchesList(matches: data.topMatches!),
          const SizedBox(height: 16),
        ],
        if (data.matchingReason != null) ...[
          _buildMatchingReason(context, data.matchingReason!),
          const SizedBox(height: 16),
        ],
        if (data.pricing != null) ...[
          PricingCard(pricing: data.pricing!),
          const SizedBox(height: 16),
        ],

        // Booking confirmation gate — hide when payment failed or already booked
        if (data.selectedProvider != null && data.pricing != null && !_bookingConfirmed && data.booking == null && data.paymentFallback == null) ...[
          _buildConfirmBookingCard(context, state.isBooking),
          const SizedBox(height: 16),
        ],

        // Show booking details only after confirmation
        if (data.booking != null && _bookingConfirmed) ...[
          BookingCard(booking: data.booking!),
          const SizedBox(height: 16),
        ],

        // Cancellation fallback card
        if (data.cancellationFallback != null && _bookingConfirmed) ...[
          _buildCancellationFallbackCard(context, data.cancellationFallback!),
          const SizedBox(height: 16),
        ],

        if (data.lifecycle != null && _bookingConfirmed) ...[
          LifecycleTimeline(lifecycle: data.lifecycle!),
          const SizedBox(height: 16),
        ],
        if (data.booking?.notifications != null && _bookingConfirmed) ...[
          NotificationsCard(notifications: data.booking!.notifications!),
          const SizedBox(height: 16),
        ],
        if (_bookingConfirmed && _providerNotifications != null && _providerNotifications!.isNotEmpty) ...[
          ProviderFeedCard(notifications: _providerNotifications!),
          const SizedBox(height: 16),
        ],
        if (data.completionEvidence != null && _bookingConfirmed) ...[
          CompletionEvidenceCard(evidence: data.completionEvidence!),
          const SizedBox(height: 16),
        ],

        if (data.agentTrace != null && data.agentTrace!.isNotEmpty) ...[
          _buildAgentTraceSummary(context, data.agentTrace!),
          const SizedBox(height: 16),
        ],

        if (data.booking != null && _bookingConfirmed) _buildFeedbackButton(context),
        const SizedBox(height: 30),
      ],
    );
  }

  // ─── Loading ──────────────────────────────────────────────
  Widget _buildLoadingState(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ScaleTransition(
            scale: _pulseAnim,
            child: Container(
              width: 72, height: 72,
              decoration: BoxDecoration(
                gradient: LinearGradient(colors: [theme.colorScheme.primary, theme.colorScheme.primary]),
                borderRadius: BorderRadius.circular(20),
                boxShadow: [BoxShadow(color: theme.colorScheme.primary.withValues(alpha: 0.3), blurRadius: 20, offset: Offset(0, 8))],
              ),
              child: Icon(Icons.smart_toy_outlined, color: theme.colorScheme.surface, size: 32),
            ),
          ),
          const SizedBox(height: 24),
          Text('AI agents are working...', style: GoogleFonts.dmSans(fontSize: 17, fontWeight: FontWeight.w600, color: theme.colorScheme.onSurface)),
          const SizedBox(height: 10),
          _buildPipelineSteps(context),
          const SizedBox(height: 20),
          SizedBox(
            width: 160,
            child: ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(minHeight: 4, backgroundColor: theme.dividerColor.withValues(alpha: 0.5), valueColor: AlwaysStoppedAnimation<Color>(theme.colorScheme.primary)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPipelineSteps(BuildContext context) {
    final theme = Theme.of(context);
    final steps = ['Intent', 'Discovery', 'Matching', 'Pricing'];
    return Wrap(
      alignment: WrapAlignment.center,
      spacing: 4,
      children: steps.asMap().entries.map((entry) {
        final isLast = entry.key == steps.length - 1;
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(entry.value, style: GoogleFonts.dmSans(fontSize: 11, color: theme.colorScheme.secondary, fontWeight: FontWeight.w500)),
            if (!isLast)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 2),
                child: Icon(Icons.chevron_right_rounded, size: 14, color: theme.dividerColor),
              ),
          ],
        );
      }).toList(),
    );
  }

  // ─── Error ────────────────────────────────────────────────
  Widget _buildErrorState(BuildContext context, String error) {
    final theme = Theme.of(context);
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 72, height: 72,
              decoration: BoxDecoration(color: Colors.red.withValues(alpha: 0.08), borderRadius: BorderRadius.circular(20)),
              child: const Icon(Icons.error_outline_rounded, size: 36, color: Colors.red),
            ),
            const SizedBox(height: 20),
            Text('Something went wrong', style: GoogleFonts.dmSans(fontSize: 18, fontWeight: FontWeight.w700, color: theme.colorScheme.onSurface)),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(color: Colors.red.withValues(alpha: 0.05), borderRadius: BorderRadius.circular(12)),
              child: Text(error, textAlign: TextAlign.center, style: GoogleFonts.dmSans(fontSize: 12, color: Colors.red[700], height: 1.4)),
            ),
            const SizedBox(height: 20),
            GestureDetector(
              onTap: () => Navigator.pop(context),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 12),
                decoration: BoxDecoration(
                  gradient: LinearGradient(colors: [theme.colorScheme.primary, theme.colorScheme.primary]),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Text('Try Again', style: GoogleFonts.dmSans(fontSize: 14, fontWeight: FontWeight.w600, color: theme.colorScheme.surface)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ─── Badges ───────────────────────────────────────────────
  Widget _buildStatusBadge(BuildContext context, String status) {
    final theme = Theme.of(context);
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(color: theme.colorScheme.surfaceContainerHighest, borderRadius: BorderRadius.circular(12), border: Border.all(color: theme.dividerColor)),
      child: Row(
        children: [
          Icon(Icons.info_outline_rounded, size: 16, color: theme.colorScheme.primary),
          const SizedBox(width: 8),
          Expanded(child: Text('Pipeline: $status', style: GoogleFonts.dmSans(fontSize: 13, fontWeight: FontWeight.w600, color: theme.colorScheme.onSurface))),
        ],
      ),
    );
  }

  Widget _buildDataSourceBadge(BuildContext context, String dataSource, bool isLive, [String? fallbackReason]) {
    final theme = Theme.of(context);
    final subtitle = isLive
        ? 'Providers found via Google Maps Places + Geocoding APIs'
        : fallbackReason != null
            ? 'Maps failed: $fallbackReason — mock fallback used'
            : 'Using pre-loaded mock providers (Maps API key missing or no results)';
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: isLive ? Colors.green.withValues(alpha: 0.06) : Colors.orange.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: isLive ? Colors.green.withValues(alpha: 0.25) : Colors.orange.withValues(alpha: 0.25)),
      ),
      child: Row(
        children: [
          Icon(isLive ? Icons.map_rounded : Icons.data_object_rounded, size: 16, color: isLive ? Colors.green[700] : Colors.orange[700]),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Data Source: $dataSource', style: GoogleFonts.dmSans(fontSize: 12, fontWeight: FontWeight.w600, color: isLive ? Colors.green[800] : Colors.orange[800])),
                Text(
                  subtitle,
                  style: GoogleFonts.dmSans(fontSize: 11, color: theme.colorScheme.onSurface.withValues(alpha: 0.6)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ─── Cards ────────────────────────────────────────────────
  Widget _buildFallbackCard(BuildContext context, Map<String, dynamic> fallback) {
    final theme = Theme.of(context);
    final message = fallback['message']?.toString() ?? 'Something went wrong.';
    final alternatives = fallback['alternatives'];
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(color: Colors.amber.withValues(alpha: 0.08), borderRadius: BorderRadius.circular(14), border: Border.all(color: Colors.amber.withValues(alpha: 0.25))),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.warning_amber_rounded, size: 18, color: Colors.amber[700]),
              const SizedBox(width: 10),
              Expanded(child: Text(message, style: GoogleFonts.dmSans(fontSize: 13, color: theme.colorScheme.onSurface, height: 1.4))),
            ],
          ),
          if (alternatives is List && alternatives.isNotEmpty) ...[
            const SizedBox(height: 12),
            Text('Suggestions:', style: GoogleFonts.dmSans(fontSize: 12, fontWeight: FontWeight.w600, color: theme.colorScheme.primary)),
            const SizedBox(height: 6),
            ...alternatives.map((alt) => Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                children: [
                  Icon(Icons.arrow_right_rounded, size: 16, color: theme.colorScheme.primary),
                  const SizedBox(width: 4),
                  Expanded(child: Text(alt.toString(), style: GoogleFonts.dmSans(fontSize: 12, color: theme.colorScheme.onSurface))),
                ],
              ),
            )),
          ],
        ],
      ),
    );
  }

  Widget _buildPaymentFallbackCard(BuildContext context, Map<String, dynamic> fallback) {
    final theme = Theme.of(context);
    final message = fallback['message']?.toString() ?? 'Payment confirmation failed.';
    final action = fallback['recommended_action']?.toString();
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.red.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.red.withValues(alpha: 0.25)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 32, height: 32,
                decoration: BoxDecoration(color: Colors.red.withValues(alpha: 0.12), borderRadius: BorderRadius.circular(9)),
                child: Icon(Icons.payment_rounded, size: 16, color: Colors.red[700]),
              ),
              const SizedBox(width: 10),
              Expanded(child: Text('Payment Failed', style: GoogleFonts.dmSans(fontSize: 14, fontWeight: FontWeight.w700, color: Colors.red[700]))),
            ],
          ),
          const SizedBox(height: 10),
          Text(message, style: GoogleFonts.dmSans(fontSize: 13, color: theme.colorScheme.onSurface, height: 1.4)),
          if (action != null) ...[
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(color: Colors.red.withValues(alpha: 0.04), borderRadius: BorderRadius.circular(10)),
              child: Row(
                children: [
                  Icon(Icons.lightbulb_outline_rounded, size: 14, color: Colors.red[400]),
                  const SizedBox(width: 8),
                  Expanded(child: Text(action, style: GoogleFonts.dmSans(fontSize: 12, fontWeight: FontWeight.w600, color: theme.colorScheme.onSurface))),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildCancellationFallbackCard(BuildContext context, Map<String, dynamic> fallback) {
    final theme = Theme.of(context);
    final cancelled = fallback['cancelled_provider']?.toString() ?? 'Unknown';
    final replacement = fallback['replacement_provider'];
    final replacementName = replacement is Map ? replacement['name']?.toString() : null;
    final status = fallback['status']?.toString() ?? '';
    final message = fallback['message']?.toString() ?? '';
    final dbInserted = fallback['database_inserted'] == true;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.deepOrange.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.deepOrange.withValues(alpha: 0.25)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 32, height: 32,
                decoration: BoxDecoration(color: Colors.deepOrange.withValues(alpha: 0.12), borderRadius: BorderRadius.circular(9)),
                child: Icon(Icons.swap_horiz_rounded, size: 18, color: Colors.deepOrange[700]),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  status == 'replacement_provider_selected' ? 'Provider Cancelled → Replacement Selected' : 'Provider Cancelled',
                  style: GoogleFonts.dmSans(fontSize: 14, fontWeight: FontWeight.w700, color: Colors.deepOrange[700]),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _buildCancellationRow(context, 'Cancelled', cancelled, Colors.red),
          if (replacementName != null)
            _buildCancellationRow(context, 'Replacement', replacementName, Colors.green),
          const SizedBox(height: 8),
          Text(message, style: GoogleFonts.dmSans(fontSize: 12, color: theme.colorScheme.onSurface, height: 1.4)),
          if (dbInserted) ...[
            const SizedBox(height: 6),
            Row(
              children: [
                Icon(Icons.check_circle_outline_rounded, size: 14, color: Colors.green[600]),
                const SizedBox(width: 6),
                Text('Waitlist record created in database', style: GoogleFonts.dmSans(fontSize: 11, color: Colors.green[700], fontWeight: FontWeight.w500)),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildCancellationRow(BuildContext context, String label, String value, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        children: [
          Container(
            width: 8, height: 8,
            decoration: BoxDecoration(color: color, shape: BoxShape.circle),
          ),
          const SizedBox(width: 8),
          Text('$label: ', style: GoogleFonts.dmSans(fontSize: 12, fontWeight: FontWeight.w600, color: Theme.of(context).colorScheme.secondary)),
          Expanded(child: Text(value, style: GoogleFonts.dmSans(fontSize: 12, fontWeight: FontWeight.w600, color: Theme.of(context).colorScheme.onSurface))),
        ],
      ),
    );
  }

  Widget _buildMatchingReason(BuildContext context, String reason) {
    final theme = Theme.of(context);
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.5), borderRadius: BorderRadius.circular(14), border: Border.all(color: theme.dividerColor.withValues(alpha: 0.5))),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.lightbulb_outline_rounded, size: 16, color: theme.colorScheme.primary),
          const SizedBox(width: 10),
          Expanded(child: Text(reason, style: GoogleFonts.dmSans(fontSize: 12, color: theme.colorScheme.onSurface, height: 1.5))),
        ],
      ),
    );
  }

  Widget _buildConfirmBookingCard(BuildContext context, bool isBooking) {
    final theme = Theme.of(context);
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: theme.dividerColor),
        boxShadow: [BoxShadow(color: theme.dividerColor.withValues(alpha: 0.5).withValues(alpha: 0.4), blurRadius: 16, offset: Offset(0, 6))],
      ),
      child: Column(
        children: [
          Container(
            width: 52, height: 52,
            decoration: BoxDecoration(color: theme.colorScheme.surfaceContainerHighest, borderRadius: BorderRadius.circular(16)),
            child: Icon(Icons.event_available_rounded, size: 28, color: theme.colorScheme.primary),
          ),
          const SizedBox(height: 14),
          Text('Ready to book?', style: GoogleFonts.dmSans(fontSize: 17, fontWeight: FontWeight.w700, color: theme.colorScheme.onSurface)),
          const SizedBox(height: 6),
          Text('Review the details above, then confirm your booking.', textAlign: TextAlign.center, style: GoogleFonts.dmSans(fontSize: 13, color: theme.colorScheme.secondary)),
          const SizedBox(height: 18),
          SizedBox(
            width: double.infinity,
            child: GestureDetector(
              onTap: isBooking ? null : _handleConfirmBooking,
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 14),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: isBooking
                        ? [theme.disabledColor, theme.disabledColor]
                        : [const Color(0xFF16A34A), const Color(0xFF22C55E)],
                  ),
                  borderRadius: BorderRadius.circular(14),
                  boxShadow: [BoxShadow(color: Colors.green.withValues(alpha: isBooking ? 0.1 : 0.3), blurRadius: 12, offset: const Offset(0, 4))],
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: isBooking
                      ? [
                          SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: theme.colorScheme.surface)),
                          const SizedBox(width: 10),
                          Text('Booking...', style: GoogleFonts.dmSans(fontSize: 15, fontWeight: FontWeight.w600, color: theme.colorScheme.surface)),
                        ]
                      : [
                          Icon(Icons.check_circle_rounded, color: theme.colorScheme.surface, size: 18),
                          const SizedBox(width: 8),
                          Text('Confirm Booking', style: GoogleFonts.dmSans(fontSize: 15, fontWeight: FontWeight.w600, color: theme.colorScheme.surface)),
                        ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAgentTraceSummary(BuildContext context, List traces) {
    final theme = Theme.of(context);
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: theme.colorScheme.surface, borderRadius: BorderRadius.circular(16), border: Border.all(color: theme.dividerColor.withValues(alpha: 0.5))),
      child: Row(
        children: [
          Container(
            width: 32, height: 32,
            decoration: BoxDecoration(color: theme.colorScheme.surfaceContainerHighest, borderRadius: BorderRadius.circular(9)),
            child: Icon(Icons.bolt_rounded, size: 16, color: theme.colorScheme.primary),
          ),
          const SizedBox(width: 10),
          Expanded(child: Text('${traces.length} agent steps completed', style: GoogleFonts.dmSans(fontSize: 13, fontWeight: FontWeight.w600, color: theme.colorScheme.onSurface))),
          GestureDetector(
            onTap: () {
              Navigator.push(context, MaterialPageRoute(
                builder: (_) => AgentTraceScreen(traces: ref.read(orchestrationProvider).response!.agentTrace!),
              ));
            },
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
              decoration: BoxDecoration(color: theme.colorScheme.surfaceContainerHighest, borderRadius: BorderRadius.circular(8)),
              child: Text('View all →', style: GoogleFonts.dmSans(fontSize: 12, fontWeight: FontWeight.w600, color: theme.colorScheme.primary)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFeedbackButton(BuildContext context) {
    final theme = Theme.of(context);
    return GestureDetector(
      onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const FeedbackScreen())),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 14),
        decoration: BoxDecoration(color: theme.colorScheme.surfaceContainerHighest, borderRadius: BorderRadius.circular(14), border: Border.all(color: theme.dividerColor)),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.rate_review_rounded, size: 18, color: theme.colorScheme.primary),
            const SizedBox(width: 8),
            Text('Leave Feedback', style: GoogleFonts.dmSans(fontSize: 14, fontWeight: FontWeight.w600, color: theme.colorScheme.primary)),
          ],
        ),
      ),
    );
  }
}
