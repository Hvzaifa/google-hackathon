class MatchingScores {
  final double? distanceScore;
  final double? ratingScore;
  final double? reviewScore;
  final double? reviewRecencyScore;
  final double? onTimeScore;
  final double? cancellationScore;
  final double? budgetScore;
  final double? complexityScore;
  final double? reputationScore;
  final double? futureMatchingImpact;

  const MatchingScores({
    this.distanceScore,
    this.ratingScore,
    this.reviewScore,
    this.reviewRecencyScore,
    this.onTimeScore,
    this.cancellationScore,
    this.budgetScore,
    this.complexityScore,
    this.reputationScore,
    this.futureMatchingImpact,
  });

  factory MatchingScores.fromJson(Map<String, dynamic> json) {
    return MatchingScores(
      distanceScore: (json['distance_score'] as num?)?.toDouble(),
      ratingScore: (json['rating_score'] as num?)?.toDouble(),
      reviewScore: (json['review_score'] as num?)?.toDouble(),
      reviewRecencyScore: (json['review_recency_score'] as num?)?.toDouble(),
      onTimeScore: (json['on_time_score'] as num?)?.toDouble(),
      cancellationScore: (json['cancellation_score'] as num?)?.toDouble(),
      budgetScore: (json['budget_score'] as num?)?.toDouble(),
      complexityScore: (json['complexity_score'] as num?)?.toDouble(),
      reputationScore: (json['reputation_score'] as num?)?.toDouble(),
      futureMatchingImpact: (json['future_matching_impact'] as num?)?.toDouble(),
    );
  }
}
