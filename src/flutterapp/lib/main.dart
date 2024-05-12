import 'package:flutter/material.dart';
import 'screens/video_player_screen.dart';
import 'screens/live_stream_page.dart';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Video Player',
      initialRoute: '/',
      routes: {
        '/': (context) => const VideoPlayerScreen(
              cameraId: 'cam1',
              rtspUrl: 'rtsp://192.168.0.101:8554/stream1',
            ),
        '/live': (context) => const LiveStreamPage(
              cameraId: 'cam2',
              rtspUrl: 'rtsp://192.168.0.101:8554/stream2',
            ),
      },
    );
  }
}
