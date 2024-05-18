// import 'package:flutter/material.dart';
// import 'package:video_player/video_player.dart';
// import 'package:http/http.dart' as http;
// import '../services/api_service.dart';

// class VideoPlayerScreen extends StatefulWidget {
//   final String cameraId;
//   final String rtspUrl;

//   const VideoPlayerScreen(
//       {super.key, required this.cameraId, required this.rtspUrl});

//   @override
//   VideoPlayerScreenState createState() => VideoPlayerScreenState();
// }

// class VideoPlayerScreenState extends State<VideoPlayerScreen>
//     with WidgetsBindingObserver {
//   VideoPlayerController? _controller;
//   final ApiService _apiService = ApiService();

//   final String _timestamp = 'timestamp: 未実装';
//   String _currentTsFile = '';
//   List<String> _segments = [];
//   int _currentSegmentIndex = 0;

//   Future<void> _updateCurrentTsFile() async {
//     final currentPosition = await _controller!.position;

//     // 再生位置から現在のセグメントを特定
//     _currentSegmentIndex =
//         await _getSegmentIndexByPosition(_segments, currentPosition!);

//     setState(() {
//       _currentTsFile = _segments[_currentSegmentIndex];
//     });
//   }

//   Future<int> _getSegmentIndexByPosition(
//       List<String> segments, Duration position) async {
//     int index = 0;
//     Duration currentTime = Duration.zero;

//     for (int i = 0; i < segments.length; i++) {
//       final segmentLine = segments[i];
//       try {
//         Duration segmentDuration = await _getSegmentDuration(segmentLine);

//         if (position >= currentTime &&
//             position < currentTime + segmentDuration) {
//           index = i;
//           break;
//         }

//         currentTime += segmentDuration;
//       } catch (e) {
//         const defaultDuration = Duration(seconds: 7);

//         if (position >= currentTime &&
//             position < currentTime + defaultDuration) {
//           index = i;
//           break;
//         }

//         currentTime += defaultDuration;
//       }
//     }

//     return index;
//   }

//   Future<void> _loadSegments() async {
//     final hlsStream = await _apiService.getStream(widget.cameraId);
//     final videoUrl = hlsStream.url;

//     // HLSプレイリストを取得
//     final response = await http.get(Uri.parse(videoUrl));
//     final playlist = response.body;

//     _segments = playlist
//         .split('\n')
//         .where((line) => line.startsWith('camera_'))
//         .toList();
//   }

//   Future<Duration> _getSegmentDuration(String segmentLine) async {
//     final hlsStream = await _apiService.getStream(widget.cameraId);
//     final videoUrl = hlsStream.url;

//     // HLSプレイリストを取得
//     final response = await http.get(Uri.parse(videoUrl));
//     final playlist = response.body;

//     List<String> lines = playlist.split('\n');
//     int index = lines.indexWhere((line) => line.contains(segmentLine));
//     if (index > 0) {
//       String previousLine = lines[index - 1].trim();
//       final extinf = previousLine.replaceAll('#EXTINF:', '').trim();
//       final durationString = extinf.split(',')[0];
//       final segmentDuration =
//           Duration(milliseconds: (double.parse(durationString) * 1000).toInt());

//       return segmentDuration;
//     } else {
//       return const Duration(milliseconds: 7500);
//     }
//   }

//   Future<void> _seekToSegment(int segmentIndex) async {
//     if (segmentIndex < 0 || segmentIndex >= _segments.length) {
//       return;
//     }

//     final segmentLine = _segments[segmentIndex];
//     final segmentDuration = await _getSegmentDuration(segmentLine);

//     final currentPosition = await _controller!.position;
//     final newPosition = currentPosition! +
//         segmentDuration * (segmentIndex - _currentSegmentIndex);

//     await _controller!.seekTo(newPosition);
//     _currentSegmentIndex = segmentIndex;
//     setState(() {
//       _currentTsFile = _segments[_currentSegmentIndex];
//     });
//   }

//   @override
//   void initState() {
//     super.initState();
//     WidgetsBinding.instance.addObserver(this);
//     _initializePlayer();
//   }

//   @override
//   void didChangeAppLifecycleState(AppLifecycleState state) {
//     if (state == AppLifecycleState.detached) {
//       _stopStream();
//     }
//   }

//   Future<void> _stopStream() async {
//     await _apiService.stopStream(widget.cameraId);
//   }

//   Future<void> _initializePlayer() async {
//     await _apiService.addCamera(widget.cameraId, widget.rtspUrl);
//     await _apiService.startStream(widget.cameraId);
//     await _loadSegments();

//     final hlsStream = await _apiService.getStream(widget.cameraId);
//     final videoUrl = hlsStream.url;

//     _controller = VideoPlayerController.networkUrl(Uri.parse(videoUrl));
//     await _controller!.initialize();
//     _controller!.addListener(() {
//       _updateCurrentTsFile();
//     });

//     setState(() {});
//   }

//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       appBar: AppBar(title: const Text('Video Player')),
//       body: Center(
//         child: _controller?.value.isInitialized ?? false
//             ? AspectRatio(
//                 aspectRatio: _controller!.value.aspectRatio,
//                 child: Stack(
//                   alignment: Alignment.bottomCenter,
//                   children: [
//                     VideoPlayer(_controller!),
//                     VideoProgressIndicator(
//                       _controller!,
//                       allowScrubbing: true,
//                     ),
//                     Positioned(
//                       top: 10,
//                       right: 10,
//                       child: Text(
//                         _timestamp,
//                         style: const TextStyle(
//                           color: Colors.white,
//                           backgroundColor: Colors.black54,
//                           fontSize: 16,
//                         ),
//                       ),
//                     ),
//                     Positioned(
//                       top: 40,
//                       right: 10,
//                       child: Text(
//                         'Current TS file: $_currentTsFile',
//                         style: const TextStyle(
//                           color: Colors.white,
//                           backgroundColor: Colors.black54,
//                           fontSize: 16,
//                         ),
//                       ),
//                     ),
//                   ],
//                 ),
//               )
//             : const CircularProgressIndicator(),
//       ),
//       bottomNavigationBar: BottomAppBar(
//         child: Row(
//           mainAxisAlignment: MainAxisAlignment.spaceEvenly,
//           children: [
//             Tooltip(
//               message: '10秒戻る',
//               child: IconButton(
//                 icon: const Icon(Icons.fast_rewind),
//                 onPressed: () {
//                   _seekToSegment(_currentSegmentIndex - 1);
//                 },
//               ),
//             ),
//             Tooltip(
//               message: _controller?.value.isPlaying ?? false ? '一時停止' : '再生',
//               child: IconButton(
//                 icon: Icon(
//                   _controller?.value.isPlaying ?? false
//                       ? Icons.pause
//                       : Icons.play_arrow,
//                 ),
//                 onPressed: () {
//                   setState(() {
//                     _controller?.value.isPlaying ?? false
//                         ? _controller?.pause()
//                         : _controller?.play();
//                   });
//                 },
//               ),
//             ),
//             Tooltip(
//               message: '10秒進む',
//               child: IconButton(
//                 icon: const Icon(Icons.fast_forward),
//                 onPressed: () {
//                   _seekToSegment(_currentSegmentIndex + 1);
//                 },
//               ),
//             ),
//             Tooltip(
//               message: 'リアルタイム再生',
//               child: IconButton(
//                 icon: const Icon(Icons.live_tv),
//                 onPressed: () {
//                   Navigator.pushNamed(context, '/live');
//                 },
//               ),
//             ),
//           ],
//         ),
//       ),
//     );
//   }

//   @override
//   void dispose() {
//     WidgetsBinding.instance.removeObserver(this);
//     _controller?.dispose();
//     super.dispose();
//   }
// }

// 参考：https://docs.flutter.dev/cookbook/plugins/play-video
// 参考：https://kazlauskas.dev/blog/flutter-app-lifecycle-listener-overview/
// 参考：https://api.flutter.dev/flutter/widgets/AppLifecycleListener-class.html

import 'dart:async';

import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';

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
  // with WidgetsBindingObserver {
  // late final AppLifecycleListener _listener;
  late VideoPlayerController _controller;
  late Future<void> _initializeVideoPlayerFuture;
  final ApiService _apiService = ApiService();
  late String videoUrl;

  @override
  void initState() {
    super.initState();
    // WidgetsBinding.instance.addObserver(this);
    // Initialize the AppLifecycleListener class and pass callbacks
    // _listener = AppLifecycleListener(
    //   onStateChange: _onStateChanged,
    // );
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
  }

  void _initializePlayer() {
    _apiService.addCamera(widget.cameraId, widget.rtspUrl);
    _apiService.startHlsStream(widget.cameraId);
    Timer.periodic(const Duration(seconds: 5),
        (Timer t) => _apiService.keepHlsStreamAlive(widget.cameraId));
    videoUrl = _apiService.getHlsStreamUrl(widget.cameraId);
  }

  // void _stopStream() {
  //   _apiService.stopStream(widget.cameraId);
  // }

  @override
  void dispose() {
    // WidgetsBinding.instance.removeObserver(this);
    // Do not forget to dispose the listener
    // _listener.dispose();
    // Ensure disposing of the VideoPlayerController to free up resources.
    _controller.dispose();
    super.dispose();
  }

  // @override
  // void didChangeAppLifecycleState(AppLifecycleState state) {
  //   if (state == AppLifecycleState.detached) {
  //     WidgetsBinding.instance.addPostFrameCallback((_) {
  //       _stopStream();
  //     });
  //   }
  // }

  // Listen to the app lifecycle state changes
  // void _onStateChanged(AppLifecycleState state) {
  //   switch (state) {
  //     case AppLifecycleState.detached:
  //       _onDetached();
  //     case AppLifecycleState.resumed:
  //       _onResumed();
  //     case AppLifecycleState.inactive:
  //       _onInactive();
  //     case AppLifecycleState.hidden:
  //       _onHidden();
  //     case AppLifecycleState.paused:
  //       _onPaused();
  //   }
  // }

  // void _onDetached() => {
  //       print('detached'),
  //       _stopStream(),
  //     };

  // void _onResumed() => print('resumed');

  // void _onInactive() => print('inactive');

  // void _onHidden() => print('hidden');

  // void _onPaused() => {
  //       print('paused'),
  //     };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Butterfly Video'),
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
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // Wrap the play or pause in a call to `setState`. This ensures the
          // correct icon is shown.
          setState(() {
            // If the video is playing, pause it.
            if (_controller.value.isPlaying) {
              _controller.pause();
            } else {
              // If the video is paused, play it.
              _controller.play();
            }
          });
        },
        // Display the correct icon depending on the state of the player.
        child: Icon(
          _controller.value.isPlaying ? Icons.pause : Icons.play_arrow,
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
                  Navigator.pushNamed(context, '/live');
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
