import 'package:flutter/material.dart';
import 'screens/rtsp_stream_screen.dart';
import 'screens/video_player_example.dart';
// import 'screens/hls_stream_video_player_screen.dart';
import 'screens/hls_stream_media_kit_screen.dart';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Video Player',
      initialRoute: '/',
      routes: {
        '/': (context) => const RTSPPlayer(
              cameraId: 'cam1',
              rtspUrl: 'rtsp://192.168.0.101:8554/stream1',
            ),
        '/hls': (context) => const HlsMediaKitPlayer(
              cameraId: 'cam1',
              rtspUrl: 'rtsp://192.168.0.101:8554/stream1',
            ),
        '/example': (context) => const VideoPlayerExample(
              cameraId: 'cam1',
              rtspUrl: 'rtsp://192.168.0.101:8554/stream1',
            ),
      },
    );
  }
}
