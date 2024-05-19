import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';

class ProgressText extends StatefulWidget {
  final VideoPlayerController controller;
  final Duration totalDuration;

  // VideoPlayerControllerを受け取れるようにする
  const ProgressText({
    super.key,
    required this.controller,
    required this.totalDuration,
  });

  @override
  ProgressTextState createState() => ProgressTextState();
}

class ProgressTextState extends State<ProgressText> {
  late VoidCallback _listener;

  ProgressTextState() {
    _listener = () {
      // 検知したタイミングで再描画する
      setState(() {});
    };
  }

  @override
  void initState() {
    super.initState();
    // VideoPlayerControllerの更新を検知できるようにする
    widget.controller.addListener(_listener);
  }

  @override
  void deactivate() {
    widget.controller.removeListener(_listener);
    super.deactivate();
  }

  @override
  Widget build(BuildContext context) {
    // 現在の値を元にUIを表示する
    final String position = widget.controller.value.position.toString();
    final String duration = widget.totalDuration.toString();
    return Text(
      '$position / $duration',
      style: const TextStyle(
        color: Colors.white,
        backgroundColor: Colors.black54,
        fontSize: 16,
      ),
    );
  }
}
