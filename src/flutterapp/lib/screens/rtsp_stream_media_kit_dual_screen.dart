import 'package:flutter/material.dart';
import 'package:media_kit/media_kit.dart';
import 'package:media_kit_video/media_kit_video.dart';
// import 'package:media_kit_libs_video/media_kit_libs_video.dart';

class RtspDualMediaKitPlayer extends StatefulWidget {
  final String cameraId1;
  final String rtspUrl1;
  final String cameraId2;
  final String rtspUrl2;

  const RtspDualMediaKitPlayer(
      {super.key,
      required this.cameraId1,
      required this.rtspUrl1,
      required this.cameraId2,
      required this.rtspUrl2});

  @override
  RtspDualMediaKitPlayerState createState() => RtspDualMediaKitPlayerState();
}

class RtspDualMediaKitPlayerState extends State<RtspDualMediaKitPlayer> {
  late final Player _player1;
  late final VideoController _controller1;
  late final Player _player2;
  late final VideoController _controller2;

  @override
  void initState() {
    super.initState();
    MediaKit.ensureInitialized();
    _player1 = Player();
    _controller1 = VideoController(_player1);
    _player1.open(Media(widget.rtspUrl1));
    _player2 = Player();
    _controller2 = VideoController(_player2);
    _player2.open(Media(widget.rtspUrl2));
  }

  @override
  void dispose() {
    _player1.dispose();
    _player2.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('RTSP Stream'),
      ),
      body: Center(
        child: Row(
          children: [
            Expanded(
              child: Video(
                controller: _controller1,
                width: MediaQuery.of(context).size.width / 2,
                height: MediaQuery.of(context).size.height,
              ),
            ),
            Expanded(
              child: Video(
                controller: _controller2,
                width: MediaQuery.of(context).size.width / 2,
                height: MediaQuery.of(context).size.height,
              ),
            ),
          ],
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
