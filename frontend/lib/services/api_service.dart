import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/orchestration_response.dart';

class ApiService {
  // Use your machine's local IP for physical device testing.
  // Use 10.0.2.2 for Android emulator, localhost for iOS simulator.
  final String baseUrl = 'http://192.168.18.11:8000/api';

  Future<OrchestrationResponse> orchestrate(
    String message, {
    String userId = 'demo_user',
    bool simulateMapsFailure = false,
    bool simulateNoProviders = false,
    bool simulateBookingFailure = false,
    bool simulatePaymentFailure = false,
    bool simulateProviderCancellation = false,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/orchestrate'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'message': message,
        'user_id': userId,
        'simulate_maps_failure': simulateMapsFailure,
        'simulate_no_providers': simulateNoProviders,
        'simulate_booking_failure': simulateBookingFailure,
        'simulate_payment_failure': simulatePaymentFailure,
        'simulate_provider_cancellation': simulateProviderCancellation,
      }),
    );

    if (response.statusCode == 200) {
      return OrchestrationResponse.fromJson(jsonDecode(response.body));
    } else {
      throw Exception(
        'Failed to orchestrate: ${response.statusCode} - ${response.body}',
      );
    }
  }

  Future<OrchestrationResponse> confirmBooking({
    required String userId,
    required Map<String, dynamic> intent,
    required Map<String, dynamic> selectedProvider,
    required Map<String, dynamic> pricing,
    required List<Map<String, dynamic>> agentTrace,
    Map<String, dynamic> simulationFlags = const {},
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/book'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': userId,
        'intent': intent,
        'selected_provider': selectedProvider,
        'pricing': pricing,
        'agent_trace': agentTrace,
        'simulation_flags': simulationFlags,
      }),
    );

    if (response.statusCode == 200) {
      return OrchestrationResponse.fromJson(jsonDecode(response.body));
    } else {
      throw Exception(
        'Booking failed: ${response.statusCode} - ${response.body}',
      );
    }
  }
}
