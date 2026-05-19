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
import 'agent_trace_screen.dart';
import 'feedback_screen.dart';

class ResultsScreen extends ConsumerStatefulWidget {
  const ResultsScreen({super.key});

  @override
  ConsumerState<ResultsScreen> createState() => _ResultsScreenState();
}

class _ResultsScreenState extends ConsumerState<ResultsScreen>
    with SingleTickerProviderStateMixin {
  bool _bookingConfirmed = false;
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

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(orchestrationProvider);
    final screenWidth = MediaQuery.of(context).size.width;
    final isTablet = screenWidth > 600;
    final horizontalPad = isTablet ? 32.0 : 16.0;

    return Scaffold(
      backgroundColor: Colors.white,
      body: Stack(
        children: [
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: Container(
              height: 260,
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [Color(0xFFF3F0FF), Colors.white],
                ),
              ),
            ),
          ),
          SafeArea(
            child: Column(
              children: [
                // Header
                Container(
                  padding: EdgeInsets.symmetric(
                      horizontal: horizontalPad, vertical: 12),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.8),
                    border: const Border(
                      bottom: BorderSide(color: AppTheme.kPurple100),
                    ),
                  ),
                  child: Row(
                    children: [
                      GestureDetector(
                        onTap: () {
                          ref.read(orchestrationProvider.notifier).reset();
                          Navigator.pop(context);
                        },
                        child: Container(
                          width: 38,
                          height: 38,
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: AppTheme.kPurple200),
                          ),
                          child: const Icon(
                            Icons.arrow_back_ios_new_rounded,
                            color: AppTheme.kPurple700,
                            size: 16,
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Text(
                        'Results',
                        style: GoogleFonts.dmSans(
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                          color: AppTheme.kPurple900,
                        ),
                      ),
                      const Spacer(),
                      if (state.response != null)
                        GestureDetector(
                          onTap: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => AgentTraceScreen(
                                  traces:
                                      state.response!.agentTrace ?? [],
                                ),
                              ),
                            );
                          },
                          child: Container(
                            width: 38,
                            height: 38,
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(12),
                              border:
                                  Border.all(color: AppTheme.kPurple200),
                            ),
                            child: const Icon(Icons.timeline_rounded,
                                color: AppTheme.kPurple700, size: 18),
                          ),
                        ),
                    ],
                  ),
                ),

                // Body
                Expanded(
                  child: _buildBody(context, state, horizontalPad),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBody(
      BuildContext context, OrchestrationState state, double hPad) {
    if (state.isLoading) {
      return _buildLoadingState();
    }

    if (state.error != null) {
      return _buildErrorState(context, state.error!);
    }

    final data = state.response;
    if (data == null) {
      return Center(
        child: Text(
          'No data available',
          style: GoogleFonts.dmSans(
            fontSize: 14,
            color: AppTheme.kPurple300,
          ),
        ),
      );
    }

    // Determine data source from agent trace
    String dataSource = 'Unknown';
    bool isGoogleMapsData = false;
    for (final trace in data.agentTrace ?? []) {
      if (trace.step?.toLowerCase() == 'discovery') {
        final tool = trace.toolCalled ?? '';
        if (tool.contains('google_maps')) {
          dataSource = 'Google Maps API (Live)';
          isGoogleMapsData = true;
        } else {
          dataSource = 'Mock / Fallback Data';
        }
        break;
      }
    }

    return ListView(
      padding: EdgeInsets.symmetric(horizontal: hPad, vertical: 16),
      children: [
        // Status + Data Source row
        if (data.status != null) _buildStatusBadge(data.status!),
        _buildDataSourceBadge(dataSource, isGoogleMapsData),

        // Fallback response
        if (data.fallbackResponse != null)
          _buildFallbackCard(data.fallbackResponse!),

        // Request Understanding
        if (data.requestUnderstanding != null) ...[
          RequestUnderstandingCard(data: data.requestUnderstanding!),
          const SizedBox(height: 16),
        ],

        // Selected Provider
        if (data.selectedProvider != null) ...[
          SelectedProviderCard(provider: data.selectedProvider!),
          const SizedBox(height: 16),
        ],

        // Top Matches
        if (data.topMatches != null && data.topMatches!.isNotEmpty) ...[
          TopMatchesList(matches: data.topMatches!),
          const SizedBox(height: 16),
        ],

        // Matching Reason
        if (data.matchingReason != null) ...[
          _buildMatchingReason(data.matchingReason!),
          const SizedBox(height: 16),
        ],

        // Pricing
        if (data.pricing != null) ...[
          PricingCard(pricing: data.pricing!),
          const SizedBox(height: 16),
        ],

        // Booking confirmation gate
        if (data.booking != null && !_bookingConfirmed) ...[
          _buildConfirmBookingCard(),
          const SizedBox(height: 16),
        ],

        // Show booking details only after confirmation
        if (data.booking != null && _bookingConfirmed) ...[
          BookingCard(booking: data.booking!),
          const SizedBox(height: 16),
        ],

        // Lifecycle — only after booking is confirmed
        if (data.lifecycle != null && _bookingConfirmed) ...[
          LifecycleTimeline(lifecycle: data.lifecycle!),
          const SizedBox(height: 16),
        ],

        // Notifications — only after booking is confirmed
        if (data.booking?.notifications != null && _bookingConfirmed) ...[
          NotificationsCard(notifications: data.booking!.notifications!),
          const SizedBox(height: 16),
        ],

        // Completion Evidence
        if (data.completionEvidence != null && _bookingConfirmed) ...[
          CompletionEvidenceCard(evidence: data.completionEvidence!),
          const SizedBox(height: 16),
        ],

        // Agent Trace summary
        if (data.agentTrace != null && data.agentTrace!.isNotEmpty) ...[
          _buildAgentTraceSummary(data.agentTrace!),
          const SizedBox(height: 16),
        ],

        // Feedback button — only after booking confirmed
        if (data.booking != null && _bookingConfirmed)
          _buildFeedbackButton(),

        const SizedBox(height: 30),
      ],
    );
  }

  // ─── Loading ──────────────────────────────────────────────
  Widget _buildLoadingState() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ScaleTransition(
            scale: _pulseAnim,
            child: Container(
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [AppTheme.kPurple400, AppTheme.kPurple700],
                ),
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.kPurple400.withValues(alpha: 0.3),
                    blurRadius: 20,
                    offset: const Offset(0, 8),
                  ),
                ],
              ),
              child: const Icon(Icons.smart_toy_outlined,
                  color: Colors.white, size: 32),
            ),
          ),
          const SizedBox(height: 24),
          Text(
            'AI agents are working...',
            style: GoogleFonts.dmSans(
              fontSize: 17,
              fontWeight: FontWeight.w600,
              color: AppTheme.kPurple900,
            ),
          ),
          const SizedBox(height: 10),
          _buildPipelineSteps(),
          const SizedBox(height: 20),
          SizedBox(
            width: 160,
            child: ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: const LinearProgressIndicator(
                minHeight: 4,
                backgroundColor: AppTheme.kPurple100,
                valueColor:
                    AlwaysStoppedAnimation<Color>(AppTheme.kPurple400),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPipelineSteps() {
    final steps = ['Intent', 'Discovery', 'Matching', 'Pricing', 'Booking'];
    return Wrap(
      alignment: WrapAlignment.center,
      spacing: 4,
      children: steps.asMap().entries.map((entry) {
        final isLast = entry.key == steps.length - 1;
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              entry.value,
              style: GoogleFonts.dmSans(
                fontSize: 11,
                color: AppTheme.kPurple300,
                fontWeight: FontWeight.w500,
              ),
            ),
            if (!isLast)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 2),
                child: Icon(Icons.chevron_right_rounded,
                    size: 14, color: AppTheme.kPurple200),
              ),
          ],
        );
      }).toList(),
    );
  }

  // ─── Error ────────────────────────────────────────────────
  Widget _buildErrorState(BuildContext context, String error) {
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                color: Colors.red.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(20),
              ),
              child: const Icon(Icons.error_outline_rounded,
                  size: 36, color: Colors.red),
            ),
            const SizedBox(height: 20),
            Text(
              'Something went wrong',
              style: GoogleFonts.dmSans(
                fontSize: 18,
                fontWeight: FontWeight.w700,
                color: AppTheme.kPurple900,
              ),
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.red.withValues(alpha: 0.05),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                error,
                textAlign: TextAlign.center,
                style: GoogleFonts.dmSans(
                  fontSize: 12,
                  color: Colors.red[700],
                  height: 1.4,
                ),
              ),
            ),
            const SizedBox(height: 20),
            GestureDetector(
              onTap: () => Navigator.pop(context),
              child: Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: 28, vertical: 12),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [AppTheme.kPurple400, AppTheme.kPurple700],
                  ),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Text(
                  'Try Again',
                  style: GoogleFonts.dmSans(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ─── Badges ───────────────────────────────────────────────
  Widget _buildStatusBadge(String status) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: AppTheme.kPurple50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.kPurple200),
      ),
      child: Row(
        children: [
          const Icon(Icons.info_outline_rounded,
              size: 16, color: AppTheme.kPurple400),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              'Pipeline: $status',
              style: GoogleFonts.dmSans(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: AppTheme.kPurple900,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDataSourceBadge(String dataSource, bool isLive) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: isLive
            ? Colors.green.withValues(alpha: 0.06)
            : Colors.orange.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isLive
              ? Colors.green.withValues(alpha: 0.25)
              : Colors.orange.withValues(alpha: 0.25),
        ),
      ),
      child: Row(
        children: [
          Icon(
            isLive ? Icons.map_rounded : Icons.data_object_rounded,
            size: 16,
            color: isLive ? Colors.green[700] : Colors.orange[700],
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Data Source: $dataSource',
                  style: GoogleFonts.dmSans(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: isLive ? Colors.green[800] : Colors.orange[800],
                  ),
                ),
                Text(
                  isLive
                      ? 'Providers found via Google Maps Places + Geocoding APIs'
                      : 'Using pre-loaded mock providers (Maps API key missing or no results)',
                  style: GoogleFonts.dmSans(
                    fontSize: 11,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ─── Cards ────────────────────────────────────────────────
  Widget _buildFallbackCard(String message) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.amber.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.amber.withValues(alpha: 0.25)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.warning_amber_rounded,
              size: 18, color: Colors.amber[700]),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              message,
              style: GoogleFonts.dmSans(
                fontSize: 13,
                color: AppTheme.kPurple900,
                height: 1.4,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMatchingReason(String reason) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.kPurple50.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.kPurple100),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.lightbulb_outline_rounded,
              size: 16, color: AppTheme.kPurple400),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              reason,
              style: GoogleFonts.dmSans(
                fontSize: 12,
                color: AppTheme.kPurple900,
                height: 1.5,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildConfirmBookingCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppTheme.kPurple200),
        boxShadow: [
          BoxShadow(
            color: AppTheme.kPurple100.withValues(alpha: 0.4),
            blurRadius: 16,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        children: [
          Container(
            width: 52,
            height: 52,
            decoration: BoxDecoration(
              color: AppTheme.kPurple50,
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Icon(Icons.event_available_rounded,
                size: 28, color: AppTheme.kPurple400),
          ),
          const SizedBox(height: 14),
          Text(
            'Ready to book?',
            style: GoogleFonts.dmSans(
              fontSize: 17,
              fontWeight: FontWeight.w700,
              color: AppTheme.kPurple900,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            'Review the details above, then confirm your booking.',
            textAlign: TextAlign.center,
            style: GoogleFonts.dmSans(
              fontSize: 13,
              color: AppTheme.kPurple300,
            ),
          ),
          const SizedBox(height: 18),
          SizedBox(
            width: double.infinity,
            child: GestureDetector(
              onTap: () => setState(() => _bookingConfirmed = true),
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 14),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF16A34A), Color(0xFF22C55E)],
                  ),
                  borderRadius: BorderRadius.circular(14),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.green.withValues(alpha: 0.3),
                      blurRadius: 12,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.check_circle_rounded,
                        color: Colors.white, size: 18),
                    const SizedBox(width: 8),
                    Text(
                      'Confirm Booking',
                      style: GoogleFonts.dmSans(
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAgentTraceSummary(List traces) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.kPurple100),
      ),
      child: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: AppTheme.kPurple50,
              borderRadius: BorderRadius.circular(9),
            ),
            child: const Icon(Icons.bolt_rounded,
                size: 16, color: AppTheme.kPurple400),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              '${traces.length} agent steps completed',
              style: GoogleFonts.dmSans(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: AppTheme.kPurple900,
              ),
            ),
          ),
          GestureDetector(
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) =>
                      AgentTraceScreen(traces: ref.read(orchestrationProvider).response!.agentTrace!),
                ),
              );
            },
            child: Container(
              padding: const EdgeInsets.symmetric(
                  horizontal: 10, vertical: 5),
              decoration: BoxDecoration(
                color: AppTheme.kPurple50,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                'View all →',
                style: GoogleFonts.dmSans(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: AppTheme.kPurple400,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFeedbackButton() {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => const FeedbackScreen()),
        );
      },
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 14),
        decoration: BoxDecoration(
          color: AppTheme.kPurple50,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: AppTheme.kPurple200),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.rate_review_rounded,
                size: 18, color: AppTheme.kPurple400),
            const SizedBox(width: 8),
            Text(
              'Leave Feedback',
              style: GoogleFonts.dmSans(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: AppTheme.kPurple700,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
