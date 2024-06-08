import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:logger/logger.dart';

import '../models/jpeg_image.dart';
import '../services/api_service.dart';

class RangeSelector extends StatefulWidget {
  const RangeSelector({super.key});

  @override
  RangeSelectorState createState() => RangeSelectorState();
}

class RangeSelectorState extends State<RangeSelector> {
  Offset? _start;
  Offset? _end;
  final List<JpegImage> _jpegImages = [];
  var logger = Logger();
  final ApiService _apiService = ApiService();
  final GlobalKey _imageKey = GlobalKey();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeFromArguments();
    });
  }

  void _initializeFromArguments() {
    final args = ModalRoute.of(context)?.settings.arguments;
    if (args is Map<String, String>) {
      setState(() {
        if (args['cameraId'] != null && args['rtspUrl'] != null) {
          JpegImage jpegImage =
              JpegImage(cameraId: args['cameraId']!, rtspUrl: args['rtspUrl']!);
          if (_jpegImages.isEmpty) {
            _jpegImages.add(jpegImage);
          } else {
            _jpegImages[0] = jpegImage;
          }
        } else {
          logger.e('Missing cameraId or rtspUrl in arguments: $args');
        }
      });
    } else {
      // 引数が期待した型でない場合のエラーハンドリング
      logger.e('Invalid arguments: $args');
    }
  }

  void _getImage() async {
    String cameraId = _jpegImages[0].cameraId;
    Uint8List jpegData = await _apiService.getLatestRecordedImage(cameraId);
    _jpegImages[0].setImage(jpegData);

    // originalWidthとoriginalHeightをセット
    final decodedImage = await decodeImageFromList(jpegData);
    setState(() {
      _jpegImages[0].originalWidth = decodedImage.width.toDouble();
      _jpegImages[0].originalHeight = decodedImage.height.toDouble();
    });
  }

  void _saveSelectionCoordinates() {
    if (_start != null && _end != null && _jpegImages.isNotEmpty) {
      final renderBox =
          _imageKey.currentContext?.findRenderObject() as RenderBox?;
      if (renderBox != null) {
        final currentStartX = _start!.dx;
        final currentStartY = _start!.dy;
        final currentEndX = _end!.dx;
        final currentEndY = _end!.dy;

        final originalStartX = (currentStartX / renderBox.size.width) *
            _jpegImages[0].originalWidth!;
        final originalStartY = (currentStartY / renderBox.size.height) *
            _jpegImages[0].originalHeight!;
        final originalEndX = (currentEndX / renderBox.size.width) *
            _jpegImages[0].originalWidth!;
        final originalEndY = (currentEndY / renderBox.size.height) *
            _jpegImages[0].originalHeight!;

        _jpegImages[0].setSelectionCoordinates(
          originalStartX: originalStartX,
          originalStartY: originalStartY,
          originalEndX: originalEndX,
          originalEndY: originalEndY,
          currentStartX: currentStartX,
          currentStartY: currentStartY,
          currentEndX: currentEndX,
          currentEndY: currentEndY,
        );
      }
    }
  }

  void _saveSelectedArea() {
    if (_jpegImages.isNotEmpty) {
      _apiService.saveSelectedArea(
        _jpegImages[0].cameraId,
        _jpegImages[0].image!,
        _jpegImages[0].originalWidth!,
        _jpegImages[0].originalHeight!,
        _jpegImages[0].originalStartX!,
        _jpegImages[0].originalStartY!,
        _jpegImages[0].originalEndX!,
        _jpegImages[0].originalEndY!,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Select Range'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
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
      body: SingleChildScrollView(
        // Wrap the Column with SingleChildScrollView
        child: Column(
          children: [
            Wrap(
              alignment: WrapAlignment.spaceEvenly,
              children: [
                IconButton(
                  iconSize: 36, // アイコンサイズを大きくする
                  icon: const Icon(
                    Icons.image,
                    color: Colors.green,
                  ),
                  tooltip: '最新録画画像取得',
                  onPressed: () => _getImage(),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                        ' Current Start: (${_jpegImages.isNotEmpty ? _jpegImages[0].currentStartX?.toStringAsFixed(2) : ""}, ${_jpegImages.isNotEmpty ? _jpegImages[0].currentStartY?.toStringAsFixed(2) : ""})'),
                    Text(
                        ' Current End: (${_jpegImages.isNotEmpty ? _jpegImages[0].currentEndX?.toStringAsFixed(2) : ""}, ${_jpegImages.isNotEmpty ? _jpegImages[0].currentEndY?.toStringAsFixed(2) : ""})'),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                        ' Original Start: (${_jpegImages.isNotEmpty ? _jpegImages[0].originalStartX?.toStringAsFixed(2) : ""}, ${_jpegImages.isNotEmpty ? _jpegImages[0].originalStartY?.toStringAsFixed(2) : ""})'),
                    Text(
                        ' Original End: (${_jpegImages.isNotEmpty ? _jpegImages[0].originalEndX?.toStringAsFixed(2) : ""}, ${_jpegImages.isNotEmpty ? _jpegImages[0].originalEndY?.toStringAsFixed(2) : ""})'),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                        ' Current width: ${_jpegImages.isNotEmpty ? _jpegImages[0].currentWidth?.toStringAsFixed(2) : ""}'),
                    Text(
                        ' Current height: ${_jpegImages.isNotEmpty ? _jpegImages[0].currentHeight?.toStringAsFixed(2) : ""}'),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                        ' Original width: ${_jpegImages.isNotEmpty ? _jpegImages[0].originalWidth?.toStringAsFixed(2) : ""}'),
                    Text(
                        ' Original height: ${_jpegImages.isNotEmpty ? _jpegImages[0].originalHeight?.toStringAsFixed(2) : ""}'),
                  ],
                ),
              ],
            ),
            Row(
              children: [
                Expanded(
                  child:
                      // 画像表示
                      Card(
                    child: Column(
                      children: [
                        const Text('最新録画画像'),
                        _jpegImages.isNotEmpty && _jpegImages[0].image != null
                            ? LayoutBuilder(
                                builder: (context, constraints) {
                                  final maxWidth =
                                      MediaQuery.of(context).size.width * 0.98;
                                  final image = GestureDetector(
                                    onPanStart: (details) {
                                      setState(() {
                                        _start = details.localPosition;
                                        _end = _start;
                                      });
                                    },
                                    onPanUpdate: (details) {
                                      setState(() {
                                        _end = details.localPosition;
                                      });
                                    },
                                    onPanEnd: (details) {
                                      _saveSelectionCoordinates();
                                      _saveSelectedArea();
                                    },
                                    child: CustomPaint(
                                      painter: _RangePainter(_start, _end),
                                      child: SizedBox(
                                        width: maxWidth,
                                        child: Stack(
                                          children: [
                                            Image.memory(
                                              _jpegImages[0].image!,
                                              key: _imageKey,
                                              fit: BoxFit.contain,
                                            ),
                                            CustomPaint(
                                              painter:
                                                  _RangePainter(_start, _end),
                                            ),
                                          ],
                                        ),
                                      ),
                                    ),
                                  );

                                  WidgetsBinding.instance
                                      .addPostFrameCallback((_) {
                                    final renderBox = _imageKey.currentContext
                                        ?.findRenderObject() as RenderBox?;
                                    if (renderBox != null) {
                                      if (mounted) {
                                        setState(() {
                                          _jpegImages[0].currentWidth =
                                              renderBox.size.width;
                                          _jpegImages[0].currentHeight =
                                              renderBox.size.height;
                                        });
                                      }
                                    }
                                  });

                                  return image;
                                },
                              )
                            : const Text('録画画像を取得してください。'),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _RangePainter extends CustomPainter {
  final Offset? start;
  final Offset? end;

  _RangePainter(this.start, this.end);

  @override
  void paint(Canvas canvas, Size size) {
    if (start != null && end != null) {
      final paint = Paint()
        ..color = Colors.blue.withOpacity(0.5)
        ..style = PaintingStyle.fill;

      final rect = Rect.fromPoints(start!, end!);
      canvas.drawRect(rect, paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return true;
  }
}
