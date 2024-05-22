import 'package:flutter/material.dart';
import 'screens/camera_register.dart';
import 'screens/rtsp_stream_media_kit_selected_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Camera App',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => const CameraRegister(),
        '/rtsp_stream': (context) => const RtspMediaKitAddPlayer(),
      },
    );
  }
}