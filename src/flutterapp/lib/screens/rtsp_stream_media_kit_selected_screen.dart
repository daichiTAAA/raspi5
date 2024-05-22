import 'package:flutter/material.dart';
import 'package:media_kit/media_kit.dart';
import 'package:media_kit_video/media_kit_video.dart';
// import 'package:media_kit_libs_video/media_kit_libs_video.dart';

import '../models/rtsp_stream_media_kit.dart';

class RtspMediaKitAddPlayer extends StatefulWidget {
  const RtspMediaKitAddPlayer({
    super.key,
  });

  @override
  RtspMediaKitAddPlayerState createState() => RtspMediaKitAddPlayerState();
}

class RtspMediaKitAddPlayerState extends State<RtspMediaKitAddPlayer> {
  final List<RtspStream> _streams = [];
  final TextEditingController _cameraIdController = TextEditingController();
  final TextEditingController _rtspUrlController = TextEditingController();

  @override
  void initState() {
    super.initState();
    MediaKit.ensureInitialized();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeFromArguments();
    });
  }

  void _initializeFromArguments() {
    final args = ModalRoute.of(context)?.settings.arguments
        as List<Map<String, String>>?;
    if (args != null) {
      setState(() {
        for (var camera in args) {
          _streams.add(RtspStream(
              cameraId: camera['camera_id']!, rtspUrl: camera['rtsp_url']!));
        }
      });
    }
  }

  @override
  void dispose() {
    for (var stream in _streams) {
      stream.player.dispose();
    }
    _cameraIdController.dispose();
    _rtspUrlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('RTSP Stream'),
        actions: [
          IconButton(
            icon: const Icon(Icons.camera),
            onPressed: () {
              Navigator.pushNamed(context, '/');
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: LayoutBuilder(
              builder: (context, constraints) {
                int crossAxisCount;
                if (constraints.maxWidth > 1200) {
                  crossAxisCount = 4; // 大画面
                } else if (constraints.maxWidth > 800) {
                  crossAxisCount = 3; // 中画面
                } else if (constraints.maxWidth > 600) {
                  crossAxisCount = 2; // 小画面
                } else {
                  crossAxisCount = 1; // それ以下
                }

                return GridView.builder(
                  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: crossAxisCount,
                    childAspectRatio: 1, // アスペクト比を調整
                  ),
                  itemCount: _streams.length,
                  itemBuilder: (context, index) {
                    final stream = _streams[index];
                    return Card(
                      child: Column(
                        children: [
                          Text('Camera ID: ${stream.cameraId}'),
                          Expanded(
                            child: SizedBox(
                              height: MediaQuery.of(context).size.height *
                                  0.3, // 高さをウィンドウサイズの30%に設定
                              child: Video(
                                controller: stream.controller,
                                width: MediaQuery.of(context).size.width,
                                height:
                                    MediaQuery.of(context).size.height * 0.3,
                              ),
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                );
              },
            ),
          ),
        ],
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
                  Navigator.pushNamed(context, '/hls');
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
