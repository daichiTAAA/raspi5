import 'dart:async';

import 'package:flutter/material.dart';
import 'package:logger/logger.dart';

import '../services/cameras_cruds.dart';
import '../services/api_service.dart';

class CameraRegister extends StatefulWidget {
  const CameraRegister({super.key});

  @override
  CameraRegisterState createState() => CameraRegisterState();
}

class CameraRegisterState extends State<CameraRegister> {
  final CamerasCruds _apiCrudsService = CamerasCruds();
  final ApiService _apiService = ApiService();
  final TextEditingController _cameraIdController = TextEditingController();
  final TextEditingController _rtspUrlController = TextEditingController();
  var logger = Logger();
  bool _isLoading = false;
  String? _message;
  List<dynamic> _cameras = [];
  final Set<Map<String, String>> _selectedCameras = {};
  final Set<String> _recordingCameras = {};

  @override
  void initState() {
    super.initState();
    _initializeScreen();
    _loadCameras();
  }

  void _initializeScreen() async {
    // 初期化処理があればここに記述
  }

  void _loadCameras() async {
    try {
      final cameras = await _apiCrudsService.getCameras();
      setState(() {
        _cameras = cameras;
      });
    } catch (e) {
      setState(() {
        _message = 'カメラの読み込みに失敗しました: $e';
      });
    }
  }

  @override
  void dispose() {
    _cameraIdController.dispose();
    _rtspUrlController.dispose();
    super.dispose();
  }

  Future<void> _registerCamera() async {
    setState(() {
      _isLoading = true;
      _message = null;
    });

    final cameraId = _cameraIdController.text;
    final rtspUrl = _rtspUrlController.text;

    if (cameraId.isEmpty || rtspUrl.isEmpty) {
      setState(() {
        _isLoading = false;
        _message = 'カメラIDとRTSP URLを入力してください';
      });
      return;
    }

    try {
      final cameraData = {
        'camera_id': cameraId,
        'rtsp_url': rtspUrl,
      };
      final response = await _apiCrudsService.createCamera(cameraData);
      setState(() {
        _message = 'カメラが正常に登録されました: ${response['camera_id']}';
        _loadCameras(); // カメラ一覧を再読み込み
      });
    } catch (e) {
      setState(() {
        _message = 'カメラの登録に失敗しました: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _toggleCameraSelection(String cameraId, String rtspUrl) {
    setState(() {
      final camera = {'camera_id': cameraId, 'rtsp_url': rtspUrl};
      final existingCamera = _selectedCameras.firstWhere(
        (selectedCamera) =>
            selectedCamera['camera_id'] == cameraId &&
            selectedCamera['rtsp_url'] == rtspUrl,
        orElse: () => {},
      );
      if (existingCamera.isNotEmpty) {
        _selectedCameras.remove(existingCamera);
      } else {
        _selectedCameras.add(camera);
      }
    });
  }

  void _playSelectedCameras() {
    Navigator.pushNamed(
      context,
      '/rtsp_stream',
      arguments: _selectedCameras.toList(),
    );
  }

  Future<void> _startRecording(String cameraId, String rtspUrl) async {
    try {
      _apiService.addCamera(cameraId, rtspUrl);
      _apiService.startJpegExtractProcess(cameraId);
      setState(() {
        _recordingCameras.add(cameraId);
      });
    } catch (e) {
      setState(() {
        _message = '録画の開始に失敗しました: $e';
      });
    }
  }

  Future<void> _stopRecording(String cameraId) async {
    try {
      _apiService.stopJpegExtractProcess(cameraId);
      setState(() {
        _recordingCameras.remove(cameraId);
      });
    } catch (e) {
      setState(() {
        _message = '録画の停止に失敗しました: $e';
      });
    }
  }

  void _toggleRecording(String cameraId, String rtspUrl) {
    if (_recordingCameras.contains(cameraId)) {
      _stopRecording(cameraId);
    } else {
      _startRecording(cameraId, rtspUrl);
    }
  }

  void _playRecordedVideos(String cameraId, String rtspUrl) {
    _apiService.addCamera(cameraId, rtspUrl);
    Navigator.pushNamed(
      context,
      '/jpeg_stream',
      arguments: {'cameraId': cameraId, 'rtspUrl': rtspUrl},
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Network Camera App'),
        actions: [
          IconButton(
            icon: const Icon(Icons.play_arrow),
            onPressed:
                _selectedCameras.isNotEmpty ? _playSelectedCameras : null,
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _cameraIdController,
              decoration: const InputDecoration(labelText: 'カメラID'),
            ),
            TextField(
              controller: _rtspUrlController,
              decoration: const InputDecoration(labelText: 'RTSP URL'),
            ),
            const SizedBox(height: 16.0),
            ElevatedButton(
              onPressed: _isLoading ? null : _registerCamera,
              child: _isLoading
                  ? const CircularProgressIndicator()
                  : const Text('カメラを登録'),
            ),
            const SizedBox(height: 16.0),
            if (_message != null) Text(_message!),
            Expanded(
              child: ListView.builder(
                itemCount: _cameras.length,
                itemBuilder: (context, index) {
                  final camera = _cameras[index];
                  final cameraId = camera['camera_id'];
                  final rtspUrl = camera['rtsp_url'];
                  final isSelected = _selectedCameras.any(
                    (selectedCamera) =>
                        selectedCamera['camera_id'] == cameraId &&
                        selectedCamera['rtsp_url'] == rtspUrl,
                  );
                  final isRecording = _recordingCameras.contains(cameraId);

                  return ListTile(
                    title: Text(
                      'カメラID: $cameraId',
                      style: TextStyle(
                        color: isSelected ? Colors.black : null, // 選択時の文字色を黒に設定
                      ),
                    ),
                    subtitle: Text(
                      'RTSP URL: $rtspUrl',
                      style: TextStyle(
                        color: isSelected ? Colors.black : null, // 選択時の文字色を黒に設定
                      ),
                    ),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Tooltip(
                          message: 'Live選択',
                          child: Checkbox(
                            value: isSelected,
                            onChanged: (bool? value) {
                              _toggleCameraSelection(cameraId, rtspUrl);
                            },
                            activeColor: Colors.blue, // チェックボックスの選択時の色を青に設定
                            checkColor: Colors.white, // チェックマークの色を白に設定
                          ),
                        ),
                        const SizedBox(width: 20), // ボタン間のスペースを追加
                        IconButton(
                          iconSize: 36, // アイコンサイズを大きくする
                          icon: Icon(
                            isRecording ? Icons.stop : Icons.videocam,
                            color: isRecording ? Colors.red : Colors.green,
                          ),
                          tooltip: isRecording ? '録画停止' : '録画開始',
                          onPressed: () => _toggleRecording(cameraId, rtspUrl),
                        ),
                        const SizedBox(width: 8), // ボタン間のスペースを追加
                        IconButton(
                          iconSize: 36, // アイコンサイズを大きくする
                          icon:
                              const Icon(Icons.play_arrow, color: Colors.green),
                          tooltip: '録画再生',
                          onPressed: () =>
                              _playRecordedVideos(cameraId, rtspUrl),
                        ),
                      ],
                    ),
                    selected: isSelected,
                    onTap: () => _toggleCameraSelection(cameraId, rtspUrl),
                  );
                },
              ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _selectedCameras.isNotEmpty ? _playSelectedCameras : null,
        tooltip: 'Live再生',
        backgroundColor:
            _selectedCameras.isNotEmpty ? Colors.green : Colors.grey,
        child: const Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.play_arrow),
            Text('Live', style: TextStyle(fontSize: 10)),
          ],
        ),
      ),
    );
  }
}
