class FeedbackResponse {
  final String? feedbackId;
  final int? rating;
  final String? comment;
  final String? status;
  final String? summary;

  const FeedbackResponse({
    this.feedbackId,
    this.rating,
    this.comment,
    this.status,
    this.summary,
  });

  factory FeedbackResponse.fromJson(Map<String, dynamic> json) {
    return FeedbackResponse(
      feedbackId: json['feedback_id'],
      rating: json['rating'],
      comment: json['comment'],
      status: json['status'],
      summary: json['summary'],
    );
  }
}
