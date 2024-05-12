class ByteStream {
  final String cameraId;
  final String url;
  final String timestamp;

  ByteStream(
      {required this.cameraId, required this.url, required this.timestamp});

  factory ByteStream.fromJson(Map<String, dynamic> json) {
    return ByteStream(
      cameraId: json['camera_id'],
      url: json['url'],
      timestamp: json['timestamp'] ?? '',
    );
  }
}
