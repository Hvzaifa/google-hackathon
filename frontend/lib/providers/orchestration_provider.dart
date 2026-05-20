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
  // Store simulation flags so they survive across Phase 1 → Phase 2
  Map<String, dynamic> _simulationFlags = {};

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
    // Persist flags for Phase 2 forwarding
    _simulationFlags = {
      'simulate_maps_failure': simulateMapsFailure,
      'simulate_no_providers': simulateNoProviders,
      'simulate_booking_failure': simulateBookingFailure,
      'simulate_payment_failure': simulatePaymentFailure,
      'simulate_provider_cancellation': simulateProviderCancellation,
    };

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

      // Serialize top matches for cancellation recovery
      final topMatchesList = (currentResponse.topMatches ?? [])
          .map((m) => <String, dynamic>{
                'name': m.name,
                'rating': m.rating,
                'distance_km': m.distanceKm,
                'final_matching_score': m.matchingScore,
                'address': m.address,
              })
          .toList();

      final bookingResponse = await api.confirmBooking(
        userId: 'demo_user',
        intent: intentMap,
        selectedProvider: providerMap,
        pricing: pricingMap,
        agentTrace: traceList,
        simulationFlags: _simulationFlags,
        topMatches: topMatchesList,
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
    _simulationFlags = {};
    state = const OrchestrationState();
  }
}

final orchestrationProvider =
    NotifierProvider<OrchestrationNotifier, OrchestrationState>(
        OrchestrationNotifier.new);