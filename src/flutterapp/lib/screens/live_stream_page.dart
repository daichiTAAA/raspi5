// import 'package:flutter/material.dart';
// import 'package:video_player/video_player.dart';
// import '../services/api_service.dart';

// class LiveStreamPage extends StatefulWidget {
//   final String cameraId;
//   final String rtspUrl;

//   const LiveStreamPage(
//       {super.key, required this.cameraId, required this.rtspUrl});

//   @override
//   LiveStreamPageState createState() => LiveStreamPageState();
// }

// class LiveStreamPageState extends State<LiveStreamPage> {
//   final ApiService _apiService = ApiService();
//   VideoPlayerController? _controller;

//   @override
//   void initState() {
//     super.initState();
//     _initializePlayer();
//   }

//   Future<void> _initializePlayer() async {
//     await _apiService.addCamera(widget.cameraId, widget.rtspUrl);
//     await _apiService.startLiveStream(widget.cameraId);
//     final videoUrl = await _apiService.getLiveStreamUrl(widget.cameraId);

//     _controller = VideoPlayerController.networkUrl(videoUrl);
//     await _controller!.initialize();
//     _controller!.play();

//     setState(() {});
//   }

//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       appBar: AppBar(title: const Text('Live Stream')),
//       body: Center(
//         child: _controller?.value.isInitialized ?? false
//             ? AspectRatio(
//                 aspectRatio: _controller!.value.aspectRatio,
//                 child: VideoPlayer(_controller!),
//               )
//             : const CircularProgressIndicator(),
//       ),
//       bottomNavigationBar: BottomAppBar(
//         child: Row(
//           mainAxisAlignment: MainAxisAlignment.spaceEvenly,
//           children: [
//             Tooltip(
//               message: '過去分再生',
//               child: IconButton(
//                 icon: const Icon(Icons.live_tv),
//                 onPressed: () {
//                   Navigator.pushNamed(context, '/');
//                 },
//               ),
//             ),
//           ],
//         ),
//       ),
//     );
//   }
// }

import 'dart:async';
import 'package:flutter/material.dart';
import '../services/api_service.dart';

class LiveStreamPage extends StatefulWidget {
  final String cameraId;
  final String rtspUrl;

  const LiveStreamPage(
      {super.key, required this.cameraId, required this.rtspUrl});

  @override
  LiveStreamPageState createState() => LiveStreamPageState();
}

class LiveStreamPageState extends State<LiveStreamPage> {
  final ApiService _apiService = ApiService();
  String? _currentImageUrl;
  String? _nextImageUrl;

  Timer? _imageTimer;

  @override
  void initState() {
    super.initState();
    _initializeStream();
  }

  Future<void> _initializeStream() async {
    await _apiService.addCamera(widget.cameraId, widget.rtspUrl);
    await _apiService.startLiveStream(widget.cameraId);
    _currentImageUrl = await _apiService.getLiveStreamUrl(widget.cameraId);
    _startImageTimer();
  }

  void _startImageTimer() {
    _imageTimer = Timer.periodic(const Duration(seconds: 1), (timer) async {
      _nextImageUrl = await _apiService.getLiveStreamUrl(widget.cameraId);
      setState(() {
        // _nextImageUrlがnullの場合は_currentImageUrlを表示する
        if (_nextImageUrl == null) {
          _nextImageUrl = _currentImageUrl;
        } else {
          _currentImageUrl = _nextImageUrl;
        }
      });
    });
  }

  @override
  void dispose() {
    _imageTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Live Stream')),
      body: Center(
        child: _currentImageUrl == null
            ? const CircularProgressIndicator()
            : AnimatedCrossFade(
                firstChild: Image.network(_currentImageUrl!),
                secondChild: _nextImageUrl == null
                    ? Container()
                    : Image.network(_nextImageUrl!),
                crossFadeState: _currentImageUrl == _nextImageUrl
                    ? CrossFadeState.showFirst
                    : CrossFadeState.showSecond,
                duration: const Duration(seconds: 1),
              ),
      ),
      bottomNavigationBar: BottomAppBar(
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            Tooltip(
              message: '過去分再生',
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
