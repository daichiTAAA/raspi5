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

  void setOriginalImageSize({required double width, required double height}) {
    originalWidth = width;
    originalHeight = height;
  }

  void setCurrentImageSize({required double width, required double height}) {
    currentWidth = width;
    currentHeight = height;
  }

  void setOriginalSelectionCoordinates({
    required double startX,
    required double startY,
    required double endX,
    required double endY,
  }) {
    originalStartX = startX;
    originalStartY = startY;
    originalEndX = endX;
    originalEndY = endY;
  }

  void setCurrentSelectionCoordinates({
    required double startX,
    required double startY,
    required double endX,
    required double endY,
  }) {
    currentStartX = startX;
    currentStartY = startY;
    currentEndX = endX;
    currentEndY = endY;
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
