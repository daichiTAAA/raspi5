import 'package:flutter/material.dart';
import 'screens/camera_register_screen.dart';
import 'screens/rtsp_stream_media_kit_selected_screen.dart';
import 'screens/jpeg_stream_media_kit_screen.dart';
import 'screens/range_selector_screen.dart';
import 'screens/saved_range_screen.dart';

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
        '/rtsp_stream': (context) => const RtspMediaKitSelectedPlayer(),
        '/jpeg_stream': (context) => const JpegStreamScreen(),
        '/range_selector': (context) => const RangeSelector(),
        '/saved_range': (context) => const SavedRangeScreen(),
      },
    );
  }
}
