import 'package:media_kit/media_kit.dart';
import 'package:media_kit_video/media_kit_video.dart';

class RtspStream {
  final String cameraId;
  final String rtspUrl;
  final Player player;
  late final VideoController controller;

  RtspStream({required this.cameraId, required this.rtspUrl})
      : player = Player() {
    controller = VideoController(player);
    player.open(Media(rtspUrl));
  }

  factory RtspStream.fromJson(Map<String, dynamic> json) {
    return RtspStream(
      cameraId: json['camera_id'],
      rtspUrl: json['rtsp_url'],
    );
  }
}