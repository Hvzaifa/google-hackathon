class LifecycleEvent {
  final String? event;
  final String? timestamp;
  final String? details;

  const LifecycleEvent({
    this.event,
    this.timestamp,
    this.details,
  });

  factory LifecycleEvent.fromJson(Map<String, dynamic> json) {
    return LifecycleEvent(
      event: json['event'],
      timestamp: json['timestamp'],
      details: json['details'],
    );
  }
}

class Lifecycle {
  final String? status;
  final String? finalStatus;
  final List<LifecycleEvent>? events;
  final String? summary;

  const Lifecycle({
    this.status,
    this.finalStatus,
    this.events,
    this.summary,
  });

  factory Lifecycle.fromJson(Map<String, dynamic> json) {
    return Lifecycle(
      status: json['status'],
      finalStatus: json['final_status'],
      events: json['events'] != null
          ? (json['events'] as List)
              .map((e) => LifecycleEvent.fromJson(e))
              .toList()
          : null,
      summary: json['summary'],
    );
  }
}
