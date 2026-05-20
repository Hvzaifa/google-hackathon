class Scheduling {
  final String? assignedSlot;
  final String? assignedDate;
  final bool? hasConflict;
  final String? summary;

  const Scheduling({
    this.assignedSlot,
    this.assignedDate,
    this.hasConflict,
    this.summary,
  });

  factory Scheduling.fromJson(Map<String, dynamic> json) {
    return Scheduling(
      assignedSlot: json['assigned_slot'],
      assignedDate: json['assigned_date'],
      hasConflict: json['has_conflict'],
      summary: json['summary'],
    );
  }
}
