import 'dart:async';

import 'package:flutter/material.dart';
import 'package:media_kit/media_kit.dart';
import 'package:media_kit_video/media_kit_video.dart';
// import 'package:media_kit_libs_video/media_kit_libs_video.dart';
import 'package:logger/logger.dart';

import '../services/api_service.dart';

class HlsMediaKitPlayer extends StatefulWidget {
  final String cameraId;
  final String rtspUrl;

  const HlsMediaKitPlayer(
      {super.key, required this.cameraId, required this.rtspUrl});

  @override
  HlsMediaKitPlayerState createState() => HlsMediaKitPlayerState();
}

class HlsMediaKitPlayerState extends State<HlsMediaKitPlayer> {
  late final Player _player;
  late final VideoController _controller;
  final ApiService _apiService = ApiService();
  late String videoUrl;
  var logger = Logger();

  @override
  void initState() {
    super.initState();
    _initializePlayer();
    MediaKit.ensureInitialized();
    _player = Player();
    _controller = VideoController(_player);
    _player.open(Media(videoUrl));
  }

  void _initializePlayer() async {
    _apiService.addCamera(widget.cameraId, widget.rtspUrl);
    _apiService.startHlsStream(widget.cameraId);
    Timer.periodic(const Duration(seconds: 5),
        (Timer t) => _apiService.keepHlsStreamAlive(widget.cameraId));
    videoUrl = _apiService.getHlsStreamUrl(widget.cameraId);
  }

  @override
  void dispose() {
    _player.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('HLS Stream Media Kit'),
      ),
      body: Center(
        child: Video(
          controller: _controller,
          width: MediaQuery.of(context).size.width,
          height: MediaQuery.of(context).size.height,
        ),
      ),
      bottomNavigationBar: BottomAppBar(
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            Tooltip(
              message: 'リアルタイム再生',
              child: IconButton(
                icon: const Icon(Icons.live_tv),
                onPressed: () {
                  Navigator.pushNamed(context, '/');
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
