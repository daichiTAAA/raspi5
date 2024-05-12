class HlsStream {
  final String cameraId;
  final String url;

  HlsStream({required this.cameraId, required this.url});

  factory HlsStream.fromJson(Map<String, dynamic> json) {
    return HlsStream(
      cameraId: json['camera_id'],
      url: json['url'],
    );
  }
}
