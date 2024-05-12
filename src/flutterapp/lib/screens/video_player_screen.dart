import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';
import 'package:http/http.dart' as http;
import '../services/api_service.dart';

class VideoPlayerScreen extends StatefulWidget {
  final String cameraId;
  final String rtspUrl;

  const VideoPlayerScreen(
      {super.key, required this.cameraId, required this.rtspUrl});

  @override
  VideoPlayerScreenState createState() => VideoPlayerScreenState();
}

class VideoPlayerScreenState extends State<VideoPlayerScreen> {
  VideoPlayerController? _controller;
  final ApiService _apiService = ApiService();

  final String _timestamp = 'timestamp: 未実装';
  String _currentTsFile = '';

  Future<void> _updateCurrentTsFile() async {
    final currentPosition = await _controller!.position;
    final hlsStream = await _apiService.getStream(widget.cameraId);
    final videoUrl = hlsStream.url;

    // HLSプレイリストを取得
    final response = await http.get(Uri.parse(videoUrl));
    final playlist = response.body;

    final segments =
        playlist.split('\n').where((line) => line.endsWith('.ts')).toList();

    // 再生位置から現在のセグメントを特定
    final currentSegmentIndex =
        _getSegmentIndexByPosition(segments, currentPosition!);

    setState(() {
      _currentTsFile = segments[currentSegmentIndex];
    });
  }

  int _getSegmentIndexByPosition(List<String> segments, Duration position) {
    int index = 0;
    Duration currentTime = Duration.zero;

    for (int i = 0; i < segments.length; i++) {
      final segmentLine = segments[i];
      final extinf =
          segmentLine.split(':')[0].replaceAll('#EXTINF:', '').trim();
      final extinfParts = extinf.split(',');
      final durationString = extinfParts[0];
      try {
        final segmentDuration = Duration(
            milliseconds: (double.parse(durationString) * 1000).toInt());

        if (position >= currentTime &&
            position < currentTime + segmentDuration) {
          index = i;
          break;
        }

        currentTime += segmentDuration;
      } catch (e) {
        continue;
      }
    }

    return index;
  }

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
    // _controller!.addListener(_updateTimestamp);
    _controller!.addListener(() {
      _updateCurrentTsFile();
    });

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
                child: Stack(
                  alignment: Alignment.bottomCenter,
                  children: [
                    VideoPlayer(_controller!),
                    VideoProgressIndicator(
                      _controller!,
                      allowScrubbing: true,
                    ),
                    Positioned(
                      top: 10,
                      right: 10,
                      child: Text(
                        _timestamp,
                        style: const TextStyle(
                          color: Colors.white,
                          backgroundColor: Colors.black54,
                          fontSize: 16,
                        ),
                      ),
                    ),
                    Positioned(
                      top: 40,
                      right: 10,
                      child: Text(
                        'Current TS file: $_currentTsFile',
                        style: const TextStyle(
                          color: Colors.white,
                          backgroundColor: Colors.black54,
                          fontSize: 16,
                        ),
                      ),
                    ),
                  ],
                ),
              )
            : const CircularProgressIndicator(),
      ),
      bottomNavigationBar: BottomAppBar(
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            Tooltip(
              message: '10秒戻る',
              child: IconButton(
                icon: const Icon(Icons.fast_rewind),
                onPressed: () {
                  _controller?.seekTo(Duration(
                      seconds: _controller!.value.position.inSeconds - 10));
                },
              ),
            ),
            Tooltip(
              message: _controller?.value.isPlaying ?? false ? '一時停止' : '再生',
              child: IconButton(
                icon: Icon(
                  _controller?.value.isPlaying ?? false
                      ? Icons.pause
                      : Icons.play_arrow,
                ),
                onPressed: () {
                  setState(() {
                    _controller?.value.isPlaying ?? false
                        ? _controller?.pause()
                        : _controller?.play();
                  });
                },
              ),
            ),
            Tooltip(
              message: '10秒進む',
              child: IconButton(
                icon: const Icon(Icons.fast_forward),
                onPressed: () {
                  _controller?.seekTo(Duration(
                      seconds: _controller!.value.position.inSeconds + 10));
                },
              ),
            ),
            Tooltip(
              message: 'リアルタイム再生',
              child: IconButton(
                icon: const Icon(Icons.live_tv),
                onPressed: () {
                  Navigator.pushNamed(context, '/live');
                },
              ),
            ),
          ],
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
