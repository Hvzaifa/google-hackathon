import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/orchestration_response.dart';
import '../services/api_service.dart';

final apiServiceProvider = Provider((ref) => ApiService());

class OrchestrationState {
  final OrchestrationResponse? response;
  final bool isLoading;
  final bool isBooking;
  final String? error;

  const OrchestrationState({
    this.response,
    this.isLoading = false,
    this.isBooking = false,
    this.error,
  });

  OrchestrationState copyWith({
    OrchestrationResponse? response,
    bool? isLoading,
    bool? isBooking,
    String? error,
  }) {
    return OrchestrationState(
      response: response ?? this.response,
      isLoading: isLoading ?? this.isLoading,
      isBooking: isBooking ?? this.isBooking,
      error: error,
    );
  }
}

class OrchestrationNotifier extends Notifier<OrchestrationState> {
  @override
  OrchestrationState build() => const OrchestrationState();

  Future<void> sendRequest(
    String message, {
    bool simulateMapsFailure = false,
    bool simulateNoProviders = false,
    bool simulateBookingFailure = false,
    bool simulatePaymentFailure = false,
    bool simulateProviderCancellation = false,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final api = ref.read(apiServiceProvider);
      final response = await api.orchestrate(
        message,
        simulateMapsFailure: simulateMapsFailure,
        simulateNoProviders: simulateNoProviders,
        simulateBookingFailure: simulateBookingFailure,
        simulatePaymentFailure: simulatePaymentFailure,
        simulateProviderCancellation: simulateProviderCancellation,
      );
      state = OrchestrationState(response: response, isLoading: false);
    } catch (e) {
      state = OrchestrationState(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> confirmBooking() async {
    final currentResponse = state.response;
    if (currentResponse == null) return;

    state = state.copyWith(isBooking: true, error: null);

    try {
      final api = ref.read(apiServiceProvider);

      // Build intent map from RequestUnderstanding
      final ru = currentResponse.requestUnderstanding;
      final intentMap = <String, dynamic>{
        'service_type': ru?.serviceType,
        'issue_description': ru?.issueDescription,
        'location': ru?.location,
        'datetime_preference': ru?.datetimePreference,
        'urgency': ru?.urgency,
        'language_detected': ru?.languageDetected,
        'confidence': ru?.confidence,
      };

      // Build provider map from SelectedProvider
      final sp = currentResponse.selectedProvider;
      final providerMap = <String, dynamic>{
        'name': sp?.name,
        'address': sp?.address,
        'rating': sp?.rating,
        'distance_km': sp?.distanceKm,
        'final_matching_score': sp?.matchingScore,
        'source': sp?.source,
      };

      // Build pricing map
      final pr = currentResponse.pricing;
      final pricingMap = <String, dynamic>{
        'status': 'calculated',
        'price': pr?.price,
        'price_range': pr?.range,
        'pricing_summary': pr?.summary,
        'breakdown': pr?.breakdown,
      };

      // Serialize existing trace
      final traceList = (currentResponse.agentTrace ?? [])
          .map((t) => t.toJson())
          .toList();

      final bookingResponse = await api.confirmBooking(
        userId: 'demo_user',
        intent: intentMap,
        selectedProvider: providerMap,
        pricing: pricingMap,
        agentTrace: traceList,
      );

      // Merge booking response into current state
      final merged = OrchestrationResponse(
        status: bookingResponse.status,
        fallbackResponse: currentResponse.fallbackResponse,
        completionEvidence: bookingResponse.completionEvidence,
        cancellationFallback: bookingResponse.cancellationFallback,
        paymentFallback: currentResponse.paymentFallback,
        requestUnderstanding: currentResponse.requestUnderstanding,
        selectedProvider: currentResponse.selectedProvider,
        topMatches: currentResponse.topMatches,
        matchingReason: currentResponse.matchingReason,
        pricing: currentResponse.pricing,
        booking: bookingResponse.booking,
        lifecycle: bookingResponse.lifecycle,
        agentTrace: bookingResponse.agentTrace,
      );

      state = OrchestrationState(response: merged, isBooking: false);
    } catch (e) {
      state = state.copyWith(
        isBooking: false,
        error: e.toString(),
      );
    }
  }

  void reset() {
    state = const OrchestrationState();
  }
}

final orchestrationProvider =
    NotifierProvider<OrchestrationNotifier, OrchestrationState>(
        OrchestrationNotifier.new);