class RequestUnderstanding {
  final String? serviceType;
  final String? issueDescription;
  final String? location;
  final String? datetimePreference;
  final String? urgency;
  final String? languageDetected;
  final double? confidence;
  final List<dynamic>? missingFields;
  final String? clarificationQuestion;

  const RequestUnderstanding({
    this.serviceType,
    this.issueDescription,
    this.location,
    this.datetimePreference,
    this.urgency,
    this.languageDetected,
    this.confidence,
    this.missingFields,
    this.clarificationQuestion,
  });

  factory RequestUnderstanding.fromJson(Map<String, dynamic> json) {
    return RequestUnderstanding(
      serviceType: json['service_type'],
      issueDescription: json['issue_description'],
      location: json['location'],
      datetimePreference: json['datetime_preference'],
      urgency: json['urgency'],
      languageDetected: json['language_detected'],
      confidence: (json['confidence'] as num?)?.toDouble(),
      missingFields: json['missing_fields'],
      clarificationQuestion: json['clarification_question'],
    );
  }
}
