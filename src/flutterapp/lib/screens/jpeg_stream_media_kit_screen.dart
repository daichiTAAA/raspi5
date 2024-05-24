import 'package:flutter/material.dart';
import 'package:media_kit/media_kit.dart';
import 'package:media_kit_video/media_kit_video.dart';
// import 'package:media_kit_libs_video/media_kit_libs_video.dart';
import 'package:logger/logger.dart';

import '../models/jpeg_stream_media_kit.dart';

import '../services/api_service.dart';

class JpegStreamScreen extends StatefulWidget {
  const JpegStreamScreen({
    super.key,
  });

  @override
  JpegStreamScreenState createState() => JpegStreamScreenState();
}

class JpegStreamScreenState extends State<JpegStreamScreen> {
  final List<JpegStream> _streams = [];
  var logger = Logger();
  final ApiService _apiService = ApiService();

  @override
  void initState() {
    super.initState();
    MediaKit.ensureInitialized();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeFromArguments();
    });
  }

  void _initializeFromArguments() {
    final args = ModalRoute.of(context)?.settings.arguments;
    if (args is Map<String, String>) {
      setState(() {
        if (args['cameraId'] != null && args['rtspUrl'] != null) {
          _apiService.addCamera(args['cameraId']!, args['rtspUrl']!);
          _streams.add(JpegStream(cameraId: args['cameraId']!));
        } else {
          logger.e('Missing cameraId or rtspUrl in arguments: $args');
        }
      });
    } else if (args is List<Map<String, String>>) {
      setState(() {
        for (var arg in args) {
          if (arg['cameraId'] != null) {
            _streams.add(JpegStream(cameraId: arg['cameraId']!));
          } else {
            logger.e('Missing cameraId in argument: $arg');
          }
        }
      });
    } else {
      // 引数が期待した型でない場合のエラーハンドリング
      logger.e('Invalid arguments: $args');
    }
  }

  @override
  void dispose() {
    for (var stream in _streams) {
      stream.player.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Jpeg Stream'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            for (JpegStream stream in _streams) {
              _apiService.stopJpegStreamProcess(stream.cameraId);
              stream.dispose();
            }
            _streams.clear();
            Navigator.pop(context);
          },
        ),
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
