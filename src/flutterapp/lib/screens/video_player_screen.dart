import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';
import '../services/api_service.dart';

class VideoPlayerScreen extends StatefulWidget {
  final String cameraId;
  final String rtspUrl;

  const VideoPlayerScreen({super.key, required this.cameraId, required this.rtspUrl});

  @override
  VideoPlayerScreenState createState() => VideoPlayerScreenState();
}

class VideoPlayerScreenState extends State<VideoPlayerScreen> {
  VideoPlayerController? _controller;
  final ApiService _apiService = ApiService();

  @override
  void initState() {
    super.initState();
    _initializePlayer();
  }

  Future<void> _initializePlayer() async {
    await _apiService.addCamera(widget.cameraId, widget.rtspUrl);
    await _apiService.startStream(widget.cameraId);
    final hlsStream = await _apiService.getStream(widget.cameraId);
    final videoUrl = hlsStream.url;
    _controller = VideoPlayerController.networkUrl(Uri.parse(videoUrl));
    await _controller!.initialize();
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Video Player')),
      body: Center(
        child: _controller?.value.isInitialized ?? false
            ? AspectRatio(
                aspectRatio: _controller!.value.aspectRatio,
                child: VideoPlayer(_controller!),
              )
            : const CircularProgressIndicator(),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          setState(() {
            _controller?.value.isPlaying ?? false
                ? _controller?.pause()
                : _controller?.play();
          });
        },
        child: Icon(
          _controller?.value.isPlaying ?? false ? Icons.pause : Icons.play_arrow,
        ),
      ),
    );
  }

  @override
  void dispose() {
    _apiService.stopStream(widget.cameraId);
    _controller?.dispose();
    super.dispose();
  }
}