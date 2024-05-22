import 'dart:async';

import 'package:flutter/material.dart';
import 'package:logger/logger.dart';

import '../services/cameras_cruds.dart';

class CameraRegister extends StatefulWidget {
  const CameraRegister({super.key});

  @override
  CameraRegisterState createState() => CameraRegisterState();
}

class CameraRegisterState extends State<CameraRegister> {
  final CamerasCruds _apiService = CamerasCruds();
  final TextEditingController _cameraIdController = TextEditingController();
  final TextEditingController _rtspUrlController = TextEditingController();
  var logger = Logger();
  bool _isLoading = false;
  String? _message;
  List<dynamic> _cameras = [];
  final Set<Map<String, String>> _selectedCameras = {};

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
      final cameras = await _apiService.getCameras();
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

    try {
      final cameraData = {
        'camera_id': _cameraIdController.text,
        'rtsp_url': _rtspUrlController.text,
      };
      final response = await _apiService.createCamera(cameraData);
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('カメラ登録'),
        actions: [
          IconButton(
            icon: const Icon(Icons.play_arrow),
            onPressed: _selectedCameras.isNotEmpty ? _playSelectedCameras : null,
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
            const SizedBox(height: 20),
            _isLoading
                ? const CircularProgressIndicator()
                : ElevatedButton(
                    onPressed: _registerCamera,
                    child: const Text('登録'),
                  ),
            const SizedBox(height: 20),
            if (_message != null) Text(_message!),
            const SizedBox(height: 20),
            Expanded(
              child: ListView.builder(
                itemCount: _cameras.length,
                itemBuilder: (context, index) {
                  final camera = _cameras[index];
                  final isSelected = _selectedCameras.any((selectedCamera) =>
                      selectedCamera['camera_id'] == camera['camera_id'] &&
                      selectedCamera['rtsp_url'] == camera['rtsp_url']);
                  return Card(
                    margin: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 16.0),
                    child: ListTile(
                      title: Text('カメラID: ${camera['camera_id']}'),
                      subtitle: Text('RTSP URL: ${camera['rtsp_url']}'),
                      trailing: Icon(
                        isSelected ? Icons.check_box : Icons.check_box_outline_blank,
                        color: isSelected ? Colors.blue : null,
                      ),
                      onTap: () => setState(() {
                        _toggleCameraSelection(camera['camera_id'], camera['rtsp_url']);
                      }),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _selectedCameras.isNotEmpty ? _playSelectedCameras : null,
        child: const Icon(Icons.play_arrow),
      ),
    );
  }
}