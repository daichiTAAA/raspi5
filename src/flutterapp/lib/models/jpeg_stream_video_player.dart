import 'package:video_player/video_player.dart';
import 'package:logger/logger.dart';

import '../services/api_service.dart';

class JpegStream {
  final String cameraId;
  static final ApiService _apiService = ApiService();
  late VideoPlayerController controller;
  var logger = Logger();

  JpegStream({required this.cameraId}) {
    final url = _apiService.getJpegStreamUrl(cameraId);
    logger.i('Initializing VideoPlayerController with URL: $url');
    controller = VideoPlayerController.networkUrl(
      Uri.parse(url),
    );
    controller.initialize().then((_) {
      controller.play();
    }).catchError((error) {
      logger.e('VideoPlayerController initialization failed: $error');
    });
  }

  factory JpegStream.fromJson(Map<String, dynamic> json) {
    return JpegStream(
      cameraId: json['camera_id'],
    );
  }
}
