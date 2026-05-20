import 'request_understanding.dart';
import 'provider.dart';
import 'pricing.dart';
import 'booking.dart';
import 'lifecycle_event.dart';
import 'agent_trace.dart';
import 'completion_evidence.dart';

class OrchestrationResponse {
  final String? status;
  final Map<String, dynamic>? fallbackResponse;
  final Map<String, dynamic>? completionEvidence;
  final Map<String, dynamic>? cancellationFallback;
  final Map<String, dynamic>? paymentFallback;

  final RequestUnderstanding? requestUnderstanding;
  final SelectedProvider? selectedProvider;
  final List<TopMatch>? topMatches;
  final String? matchingReason;

  final Pricing? pricing;
  final Booking? booking;
  final Lifecycle? lifecycle;
  final List<AgentTrace>? agentTrace;

  const OrchestrationResponse({
    this.status,
    this.fallbackResponse,
    this.completionEvidence,
    this.cancellationFallback,
    this.paymentFallback,
    this.requestUnderstanding,
    this.selectedProvider,
    this.topMatches,
    this.matchingReason,
    this.pricing,
    this.booking,
    this.lifecycle,
    this.agentTrace,
  });

  factory OrchestrationResponse.fromJson(Map<String, dynamic> json) {
    return OrchestrationResponse(
      status: json['status'],
      fallbackResponse: json['fallback_response'],
      completionEvidence: json['completion_evidence'],
      cancellationFallback: json['cancellation_fallback'],
      paymentFallback: json['payment_fallback'],
      requestUnderstanding: json['request_understanding'] != null
          ? RequestUnderstanding.fromJson(json['request_understanding'])
          : null,
      selectedProvider: json['selected_provider'] != null
          ? SelectedProvider.fromJson(json['selected_provider'])
          : null,
      topMatches: json['top_matches'] != null
          ? (json['top_matches'] as List)
              .map((i) => TopMatch.fromJson(i))
              .toList()
          : null,
      matchingReason: json['matching_reason'],
      pricing:
          json['pricing'] != null ? Pricing.fromJson(json['pricing']) : null,
      booking:
          json['booking'] != null ? Booking.fromJson(json['booking']) : null,
      lifecycle: json['lifecycle'] != null
          ? Lifecycle.fromJson(json['lifecycle'])
          : null,
      agentTrace: json['agent_trace'] != null
          ? (json['agent_trace'] as List)
              .map((i) => AgentTrace.fromJson(i))
              .toList()
          : null,
    );
  }
}
