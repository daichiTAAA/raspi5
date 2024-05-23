import 'dart:async';

import 'package:media_kit/media_kit.dart';
import 'package:media_kit_video/media_kit_video.dart';

import '../services/api_service.dart';

class JpegStream {
  final String cameraId;
  final Player player;
  late final VideoController controller;
  static final ApiService _apiService = ApiService();

  JpegStream({required this.cameraId}) : player = Player() {
    controller = VideoController(player);
    player.open(Media(_apiService.getJpegStreamUrl(cameraId)));
    Timer.periodic(const Duration(seconds: 5),
        (Timer t) => _apiService.keepJpegStreamProcessAlive(cameraId));
  }

  factory JpegStream.fromJson(Map<String, dynamic> json) {
    return JpegStream(
      cameraId: json['camera_id'],
    );
  }
}
