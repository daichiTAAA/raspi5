import 'dart:convert';
import 'package:http/http.dart' as http;

class CamerasCruds {
  static const String baseUrl = 'http://localhost:8100';

  Future<List<dynamic>> getCameras() async {
    final response = await http.get(Uri.parse('$baseUrl/v1/cameras'));
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to load cameras');
    }
  }

  Future<Map<String, dynamic>> getCameraById(String cameraId) async {
    final response = await http.get(Uri.parse('$baseUrl/v1/cameras/$cameraId'));
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to load camera');
    }
  }

  Future<Map<String, dynamic>> createCamera(
      Map<String, dynamic> cameraData) async {
    // 既存のカメラをチェック
    final existingCameras = await getCameras();
    final existingCamera = existingCameras.firstWhere(
      (camera) => camera['camera_id'] == cameraData['camera_id'],
      orElse: () => null,
    );

    if (existingCamera != null) {
      throw Exception('カメラIDが既に登録されています');
    }

    final response = await http.post(
      Uri.parse('$baseUrl/v1/cameras'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(cameraData),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to create camera');
    }
  }

  Future<Map<String, dynamic>> updateCamera(
      String cameraId, Map<String, dynamic> cameraData) async {
    final response = await http.put(
      Uri.parse('$baseUrl/v1/cameras/$cameraId'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(cameraData),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to update camera');
    }
  }

  Future<void> deleteCamera(String cameraId) async {
    final response =
        await http.delete(Uri.parse('$baseUrl/v1/cameras/$cameraId'));
    if (response.statusCode != 200) {
      throw Exception('Failed to delete camera');
    }
  }
}
