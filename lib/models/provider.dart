import 'matching_scores.dart';

class SelectedProvider {
  final String? name;
  final String? address;
  final double? rating;
  final double? distanceKm;
  final double? matchingScore;
  final String? source;

  const SelectedProvider({
    this.name,
    this.address,
    this.rating,
    this.distanceKm,
    this.matchingScore,
    this.source,
  });

  factory SelectedProvider.fromJson(Map<String, dynamic> json) {
    return SelectedProvider(
      name: json['name'],
      address: json['address'],
      rating: (json['rating'] as num?)?.toDouble(),
      distanceKm: (json['distance_km'] as num?)?.toDouble(),
      matchingScore: (json['matching_score'] as num?)?.toDouble(),
      source: json['source'],
    );
  }
}

class TopMatch {
  final String? name;
  final double? rating;
  final double? distanceKm;
  final double? matchingScore;
  final String? address;
  final MatchingScores? matchingScores;

  const TopMatch({
    this.name,
    this.rating,
    this.distanceKm,
    this.matchingScore,
    this.address,
    this.matchingScores,
  });

  factory TopMatch.fromJson(Map<String, dynamic> json) {
    return TopMatch(
      name: json['name'],
      rating: (json['rating'] as num?)?.toDouble(),
      distanceKm: (json['distance_km'] as num?)?.toDouble(),
      matchingScore: (json['matching_score'] as num?)?.toDouble(),
      address: json['address'],
      matchingScores: json['matching_scores'] != null
          ? MatchingScores.fromJson(json['matching_scores'])
          : null,
    );
  }
}
