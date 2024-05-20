// 参考：https://docs.flutter.dev/cookbook/plugins/play-video
// 参考：https://kazlauskas.dev/blog/flutter-app-lifecycle-listener-overview/
// 参考：https://api.flutter.dev/flutter/widgets/AppLifecycleListener-class.html
// 参考：https://www.flutter-study.dev/create-app/media-player

import 'dart:async';

import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';
import 'package:http/http.dart' as http;
import 'package:logger/logger.dart';

import '../services/api_service.dart';
import 'progress_text.dart';

class VideoPlayerScreen extends StatefulWidget {
  final String cameraId;
  final String rtspUrl;

  const VideoPlayerScreen(
      {super.key, required this.cameraId, required this.rtspUrl});

  @override
  VideoPlayerScreenState createState() => VideoPlayerScreenState();
}

class VideoPlayerScreenState extends State<VideoPlayerScreen> {
  late final AppLifecycleListener _listener;
  late Timer _timer;
  late VideoPlayerController _controller;
  late Future<void> _initializeVideoPlayerFuture;
  final ApiService _apiService = ApiService();
  late String videoUrl;
  var logger = Logger();
  final List<Duration> _segmentDurations = [];
  Duration _totalDuration = Duration.zero;

  String _currentTsFile = '';
  List<String> _segments = [];
  int _currentSegmentIndex = 0;

  Future<void> _updateCurrentTsFile() async {
    final currentPosition = await _controller.position;

    // 再生位置から現在のセグメントを特定
    _currentSegmentIndex =
        await _getSegmentIndexByPosition(_segments, currentPosition!);

    setState(() {
      _currentTsFile = _segments[_currentSegmentIndex];
      _currentSegmentIndex = _currentSegmentIndex;
    });
  }

  Future<int> _getSegmentIndexByPosition(
      List<String> segments, Duration position) async {
    int index = 0;
    Duration currentTime = Duration.zero;

    for (int i = 0; i < segments.length; i++) {
      final segmentLine = segments[i];
      try {
        Duration segmentDuration = await _getSegmentDuration(segmentLine);

        if (position >= currentTime &&
            position < currentTime + segmentDuration) {
          index = i;
          break;
        }

        currentTime += segmentDuration;
      } catch (e) {
        const defaultDuration = Duration(microseconds: 7500);

        if (position >= currentTime &&
            position < currentTime + defaultDuration) {
          index = i;
          break;
        }

        currentTime += defaultDuration;
      }
    }

    return index;
  }

  Future<void> _loadSegments() async {
    final videoUrl = _apiService.getHlsStreamUrl(widget.cameraId);

    // HLSプレイリストを取得
    final response = await http.get(Uri.parse(videoUrl));
    final playlist = response.body;

    _segments = playlist
        .split('\n')
        .where((line) => line.startsWith('camera_'))
        .toList();

    _totalDuration = Duration.zero;

    final lines = playlist.split('\n');
    logger.d('lines: $lines');
    for (var line in lines) {
      if (line.startsWith('#EXTINF')) {
        final durationString = line.split(':')[1].split(',')[0];
        final segmentDuration = Duration(
            milliseconds: (double.parse(durationString) * 1000).toInt());
        _segmentDurations.add(segmentDuration);
        _totalDuration += segmentDuration;
      }
    }
    logger.d('totalDuration: $_totalDuration');
    setState(() {});
  }

  Future<Duration> _getSegmentDuration(String segmentLine) async {
    final videoUrl = _apiService.getHlsStreamUrl(widget.cameraId);

    // HLSプレイリストを取得
    final response = await http.get(Uri.parse(videoUrl));
    final playlist = response.body;

    List<String> lines = playlist.split('\n');
    int index = lines.indexWhere((line) => line.contains(segmentLine));
    if (index > 0) {
      String previousLine = lines[index - 1].trim();
      final extinf = previousLine.replaceAll('#EXTINF:', '').trim();
      final durationString = extinf.split(',')[0];
      final segmentDuration =
          Duration(milliseconds: (double.parse(durationString) * 1000).toInt());

      return segmentDuration;
    } else {
      return const Duration(milliseconds: 7500);
    }
  }

  Future<void> _seekForward(Duration fastForwardTime) async {
    final currentPosition = await _controller.position;
    final newPosition = currentPosition! + fastForwardTime;

    // ビデオの長さを超えないようにする
    final videoDuration = _controller.value.duration;
    logger.d('videoDuration: $videoDuration');
    logger.d('totalDuration: $_totalDuration');
    logger.d('currentPosition: $currentPosition');
    logger.d('newPosition: $newPosition');
    if (newPosition > _totalDuration) {
      await _controller.seekTo(_totalDuration);
    } else {
      await _controller.seekTo(newPosition);
    }
  }

  @override
  void initState() {
    super.initState();
    // Initialize the AppLifecycleListener class and pass callbacks
    _listener = AppLifecycleListener(
      onStateChange: _onStateChanged,
    );
    _initializePlayer();
    // Create and store the VideoPlayerController. The VideoPlayerController
    // offers several different constructors to play videos from assets, files,
    // or the internet.
    _controller = VideoPlayerController.networkUrl(
      Uri.parse(videoUrl),
    );
    // Initialize the controller and store the Future for later use.
    _initializeVideoPlayerFuture = _controller.initialize();
    _initializeVideoPlayerFuture.then((_) {
      _controller.play();
      if (_controller.value.isPlaying) {
        setState(() {}); // アイコンを更新
      }
    });
    // Use the controller to loop the video.
    _controller.setLooping(true);
    _startPeriodicUpdates();
  }

  void _initializePlayer() async {
    _apiService.addCamera(widget.cameraId, widget.rtspUrl);
    _apiService.startHlsStream(widget.cameraId);
    Timer.periodic(const Duration(seconds: 5),
        (Timer t) => _apiService.keepHlsStreamAlive(widget.cameraId));
    videoUrl = _apiService.getHlsStreamUrl(widget.cameraId);
    await _loadSegments();
    await _updateCurrentTsFile();
  }

  void _startPeriodicUpdates() {
    const duration = Duration(seconds: 3); // 指定した秒数ごとに実行する
    _timer = Timer.periodic(duration, (Timer t) async {
      await _loadSegments();
      await _updateCurrentTsFile();
    });
  }

  @override
  void dispose() {
    // WidgetsBinding.instance.removeObserver(this);
    // Do not forget to dispose the listener
    _listener.dispose();
    // Ensure disposing of the VideoPlayerController to free up resources.
    _timer.cancel(); // タイマーを解除
    _controller.dispose();
    super.dispose();
  }

  // Listen to the app lifecycle state changes
  void _onStateChanged(AppLifecycleState state) {
    switch (state) {
      case AppLifecycleState.detached:
        _onDetached();
      case AppLifecycleState.resumed:
        _onResumed();
      case AppLifecycleState.inactive:
        _onInactive();
      case AppLifecycleState.hidden:
        _onHidden();
      case AppLifecycleState.paused:
        _onPaused();
    }
  }

  void _onDetached() => {};

  void _onResumed() => {};

  void _onInactive() => {};

  void _onHidden() => {};

  void _onPaused() => {};

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('HLS Video'),
      ),
      // Use a FutureBuilder to display a loading spinner while waiting for the
      // VideoPlayerController to finish initializing.
      body: FutureBuilder(
        future: _initializeVideoPlayerFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.done) {
            // If the VideoPlayerController has finished initialization, use
            // the data it provides to limit the aspect ratio of the video.
            return AspectRatio(
              aspectRatio: _controller.value.aspectRatio,
              // Use the VideoPlayer widget to display the video.
              child: Stack(
                children: [
                  VideoPlayer(_controller),
                  Align(
                    alignment: Alignment.bottomCenter,
                    child: VideoProgressIndicator(
                      _controller,
                      allowScrubbing: true, // スライドバーでの再生位置変更を許可
                    ),
                  ),
                  Positioned(
                    top: 10,
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
                  Positioned(
                    top: 30,
                    right: 10,
                    child: Text(
                      'Current Segment Index: $_currentSegmentIndex',
                      style: const TextStyle(
                        color: Colors.white,
                        backgroundColor: Colors.black54,
                        fontSize: 16,
                      ),
                    ),
                  ),
                  Positioned(
                    bottom: 10,
                    right: 10,
                    child: ProgressText(
                        controller: _controller,
                        totalDuration:
                            _totalDuration), // ここで_ProgressTextウィジェットを使用
                  ),
                ],
              ),
            );
          } else {
            // If the VideoPlayerController is still initializing, show a
            // loading spinner.
            return const Center(
              child: CircularProgressIndicator(),
            );
          }
        },
      ),
      bottomNavigationBar: BottomAppBar(
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            Tooltip(
              message: '巻き戻し',
              child: IconButton(
                icon: const Icon(Icons.fast_rewind),
                onPressed: () {
                  _controller.seekTo(
                      _controller.value.position - const Duration(seconds: 10));
                },
              ),
            ),
            Tooltip(
              message: _controller.value.isPlaying ? '一時停止' : '再生',
              child: IconButton(
                icon: Icon(
                  _controller.value.isPlaying ? Icons.pause : Icons.play_arrow,
                ),
                onPressed: () {
                  setState(() {
                    _controller.value.isPlaying
                        ? _controller.pause()
                        : _controller.play();
                  });
                },
              ),
            ),
            Tooltip(
              message: '早送り',
              child: IconButton(
                icon: const Icon(Icons.fast_forward),
                onPressed: () {
                  const Duration fastForwardTime = Duration(seconds: 10);
                  _seekForward(fastForwardTime);
                },
              ),
            ),
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
