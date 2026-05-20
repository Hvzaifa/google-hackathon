class Pricing {
  final num? price;
  final String? currency;
  final Map<String, dynamic>? range;
  final String? summary;
  final Map<String, dynamic>? breakdown;

  const Pricing({
    this.price,
    this.currency,
    this.range,
    this.summary,
    this.breakdown,
  });

  factory Pricing.fromJson(Map<String, dynamic> json) {
    return Pricing(
      price: json['price'],
      currency: json['currency'],
      range: json['range'],
      summary: json['summary'],
      breakdown: json['breakdown'],
    );
  }
}
