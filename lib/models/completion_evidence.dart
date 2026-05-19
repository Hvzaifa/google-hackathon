class CompletionEvidence {
  final String? status;
  final String? photoUrl;
  final String? signatureUrl;
  final String? summary;

  const CompletionEvidence({
    this.status,
    this.photoUrl,
    this.signatureUrl,
    this.summary,
  });

  factory CompletionEvidence.fromJson(Map<String, dynamic> json) {
    return CompletionEvidence(
      status: json['status'],
      photoUrl: json['photo_url'],
      signatureUrl: json['signature_url'],
      summary: json['summary'],
    );
  }
}
