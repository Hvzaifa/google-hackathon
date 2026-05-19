import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/orchestration_response.dart';
import '../services/api_service.dart';

final apiServiceProvider = Provider((ref) => ApiService());

class OrchestrationState {
  final OrchestrationResponse? response;
  final bool isLoading;
  final String? error;

  const OrchestrationState({
    this.response,
    this.isLoading = false,
    this.error,
  });

  OrchestrationState copyWith({
    OrchestrationResponse? response,
    bool? isLoading,
    String? error,
  }) {
    return OrchestrationState(
      response: response ?? this.response,
      isLoading: isLoading ?? this.isLoading,
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

  void reset() {
    state = const OrchestrationState();
  }
}

final orchestrationProvider =
    NotifierProvider<OrchestrationNotifier, OrchestrationState>(
        OrchestrationNotifier.new);
