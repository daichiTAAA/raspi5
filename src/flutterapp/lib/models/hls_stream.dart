class HlsStream {
  final String cameraId;
  final String url;
  final String timestamp;

  HlsStream({required this.cameraId, required this.url, required this.timestamp});

  factory HlsStream.fromJson(Map<String, dynamic> json) {
    return HlsStream(
      cameraId: json['camera_id'],
      url: json['url'],
      timestamp: json['timestamp'] ?? '',
    );
  }
}