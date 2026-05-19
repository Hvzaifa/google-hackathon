class Booking {
  final String? bookingId;
  final String? status;
  final num? etaMinutes;
  final Map<String, dynamic>? scheduling;
  final Map<String, dynamic>? calendar;
  final Map<String, dynamic>? notifications;
  final Map<String, dynamic>? providerOptimization;
  final Map<String, dynamic>? payment;
  final String? summary;
  final bool? databaseInserted;

  const Booking({
    this.bookingId,
    this.status,
    this.etaMinutes,
    this.scheduling,
    this.calendar,
    this.notifications,
    this.providerOptimization,
    this.payment,
    this.summary,
    this.databaseInserted,
  });

  factory Booking.fromJson(Map<String, dynamic> json) {
    return Booking(
      bookingId: json['booking_id'],
      status: json['status'],
      etaMinutes: json['eta_minutes'],
      scheduling: json['scheduling'],
      calendar: json['calendar'],
      notifications: json['notifications'],
      providerOptimization: json['provider_optimization'],
      payment: json['payment'],
      summary: json['summary'],
      databaseInserted: json['database_inserted'],
    );
  }
}
