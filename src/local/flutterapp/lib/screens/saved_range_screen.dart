import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:logger/logger.dart';

import '../models/jpeg_image.dart';
import '../models/save_area.dart';
import '../services/api_service.dart';

class SavedRangeScreen extends StatefulWidget {
  const SavedRangeScreen({super.key});

  @override
  SavedRangeScreenState createState() => SavedRangeScreenState();
}

class SavedRangeScreenState extends State<SavedRangeScreen> {
  var logger = Logger();
  final ApiService _apiService = ApiService();
  final List<JpegImage> _jpegImages = [];

  double imageWidth = 10;
  double imageHeight = 10;

  double aspectRatio = 1.0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeFromArguments().then((_) => _updateImageSize());
    });
  }

  Future<void> _initializeFromArguments() async {
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
      await _getOriginalSelectionCoordinates();
      _getCurrentImageSize();
      _getCurrentSelectionCoordinates();
    } else {
      // 引数が期待した型でない場合のエラーハンドリング
      logger.e('Invalid arguments: $args');
    }
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _updateImageSize();
  }

  void _updateImageSize() {
    if (_jpegImages.isNotEmpty) {
      setState(() {
        imageWidth = MediaQuery.of(context).size.width * 0.98;
        imageHeight = imageWidth / aspectRatio;
      });
      _getCurrentImageSize();
      _getCurrentSelectionCoordinates();
    }
  }

  Future<void> _getOriginalSelectionCoordinates() async {
    String cameraId = _jpegImages[0].cameraId;
    final SaveAreaResponse response =
        await _apiService.getSelectedArea(cameraId);

    // 画像をuint8Listに変換
    Uint8List jpegData = base64Decode(response.areaSelectedJpegData);

    setState(() {
      _jpegImages[0].setImage(jpegData);
      // 画像のサイズを格納
      _jpegImages[0].setOriginalImageSize(
        width: double.parse(response.areaSelectedJpegWidth),
        height: double.parse(response.areaSelectedJpegHeight),
      );
      // aspectRatioを計算
      aspectRatio = double.parse(response.areaSelectedJpegWidth) /
          double.parse(response.areaSelectedJpegHeight);
      // 範囲を格納
      _jpegImages[0].setOriginalSelectionCoordinates(
        startX: double.parse(response.selectedAreaStartX),
        startY: double.parse(response.selectedAreaStartY),
        endX: double.parse(response.selectedAreaEndX),
        endY: double.parse(response.selectedAreaEndY),
      );
    });
  }

  void _getCurrentImageSize() {
    double width = imageWidth;
    double height = imageHeight;

    setState(() {
      _jpegImages[0].setCurrentImageSize(width: width, height: height);
    });
  }

  void _getCurrentSelectionCoordinates() {
    double originalWidth = _jpegImages[0].originalWidth!;
    double originalHeight = _jpegImages[0].originalHeight!;
    double currentWidth = _jpegImages[0].currentWidth!;
    double currentHeight = _jpegImages[0].currentHeight!;
    double originalStartX = _jpegImages[0].originalStartX!;
    double originalStartY = _jpegImages[0].originalStartY!;
    double originalEndX = _jpegImages[0].originalEndX!;
    double originalEndY = _jpegImages[0].originalEndY!;

    double currentStartX = originalStartX * (currentWidth / originalWidth);
    double currentStartY = originalStartY * (currentHeight / originalHeight);
    double currentEndX = originalEndX * (currentWidth / originalWidth);
    double currentEndY = originalEndY * (currentHeight / originalHeight);

    setState(() {
      _jpegImages[0].setCurrentSelectionCoordinates(
        startX: currentStartX,
        startY: currentStartY,
        endX: currentEndX,
        endY: currentEndY,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
          title: const Text('Saved Range'),
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            onPressed: () {
              Navigator.pop(context);
            },
          ),
        ),
        body: SingleChildScrollView(
            child: Column(children: [
          Center(
            child: _jpegImages.isNotEmpty && _jpegImages[0].image != null
                ? Stack(
                    children: [
                      Image.memory(
                        _jpegImages[0].image!,
                        width: imageWidth,
                        height: imageHeight,
                      ),
                      CustomPaint(
                        painter: _RangePainter(
                          Offset(_jpegImages[0].currentStartX!,
                              _jpegImages[0].currentStartY!),
                          Offset(_jpegImages[0].currentEndX!,
                              _jpegImages[0].currentEndY!),
                          imageWidth,
                          imageHeight,
                        ),
                        child: SizedBox(
                          width: imageWidth,
                          height: imageHeight,
                        ),
                      ),
                    ],
                  )
                : const Text('No image available.'),
          ),
          Wrap(
            alignment: WrapAlignment.spaceEvenly,
            children: [
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
        ])));
  }
}

class _RangePainter extends CustomPainter {
  final Offset start;
  final Offset end;
  final double imageWidth;
  final double imageHeight;

  _RangePainter(this.start, this.end, this.imageWidth, this.imageHeight);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.blue.withOpacity(0.5)
      ..style = PaintingStyle.fill;

    // 画像の左上を原点として座標を計算
    final rect = Rect.fromPoints(
      Offset(start.dx * size.width / imageWidth,
          start.dy * size.height / imageHeight),
      Offset(
          end.dx * size.width / imageWidth, end.dy * size.height / imageHeight),
    );
    canvas.drawRect(rect, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return true;
  }
}
