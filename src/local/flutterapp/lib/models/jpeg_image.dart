import 'dart:typed_data';

class JpegImage {
  final String cameraId;
  final String rtspUrl;
  Uint8List? image;
  double? originalWidth;
  double? originalHeight;
  double? currentWidth;
  double? currentHeight;
  double? originalStartX;
  double? originalStartY;
  double? originalEndX;
  double? originalEndY;
  double? currentStartX;
  double? currentStartY;
  double? currentEndX;
  double? currentEndY;

  JpegImage({required this.cameraId, required this.rtspUrl});

  void setImage(Uint8List jpegData) {
    image = jpegData;
  }

  void setSelectionCoordinates({
    required double originalStartX,
    required double originalStartY,
    required double originalEndX,
    required double originalEndY,
    required double currentStartX,
    required double currentStartY,
    required double currentEndX,
    required double currentEndY,
  }) {
    this.originalStartX = originalStartX;
    this.originalStartY = originalStartY;
    this.originalEndX = originalEndX;
    this.originalEndY = originalEndY;
    this.currentStartX = currentStartX;
    this.currentStartY = currentStartY;
    this.currentEndX = currentEndX;
    this.currentEndY = currentEndY;
  }

  factory JpegImage.fromJson(Map<String, dynamic> json) {
    return JpegImage(
      cameraId: json['camera_id'],
      rtspUrl: json['rtsp_url'],
    );
  }
}