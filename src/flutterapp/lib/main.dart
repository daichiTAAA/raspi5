import 'package:flutter/material.dart';
import 'screens/video_player_screen.dart';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      title: 'HLS Video Player',
      home: VideoPlayerScreen(
        cameraId: 'cam1',
        rtspUrl: 'rtsp://192.168.0.101:8554/stream1',
      ),
    );
  }
}