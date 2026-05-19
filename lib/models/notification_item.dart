class NotificationItem {
  final String? type;
  final String? message;
  final String? channel;
  final String? timestamp;

  const NotificationItem({
    this.type,
    this.message,
    this.channel,
    this.timestamp,
  });

  factory NotificationItem.fromJson(Map<String, dynamic> json) {
    return NotificationItem(
      type: json['type'],
      message: json['message'],
      channel: json['channel'],
      timestamp: json['timestamp'],
    );
  }
}
