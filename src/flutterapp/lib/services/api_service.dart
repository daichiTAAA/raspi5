import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/hls_stream.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8100';

  Future<void> addCamera(String cameraId, String rtspUrl) async {
    final response = await http.post(
      Uri.parse('$baseUrl/v1/cameras'),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(<String, String>{
        'camera_id': cameraId,
        'rtsp_url': rtspUrl,
      }),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to add camera');
    }
  }

  Future<void> startStream(String cameraId) async {
    final response =
        await http.post(Uri.parse('$baseUrl/v1/cameras/$cameraId/start'));

    if (response.statusCode != 200) {
      throw Exception('Failed to start stream');
    }
  }

  Future<HlsStream> getStream(String cameraId) async {
    final response =
        await http.get(Uri.parse('$baseUrl/v1/cameras/$cameraId/stream'));

    if (response.statusCode == 200) {
      final jsonResponse = json.decode(response.body);
      return HlsStream.fromJson(jsonResponse);
    } else {
      throw Exception('Failed to load HLS stream');
    }
  }

  Future<void> stopStream(String cameraId) async {
    final response =
        await http.post(Uri.parse('$baseUrl/v1/cameras/$cameraId/stop'));

    if (response.statusCode != 200) {
      throw Exception('Failed to stop stream');
    }
  }

  Future<void> removeCamera(String cameraId) async {
    final response =
        await http.delete(Uri.parse('$baseUrl/v1/cameras/$cameraId'));

    if (response.statusCode != 200) {
      throw Exception('Failed to remove camera');
    }
  }

  Future<void> startLiveStream(String cameraId) async {
    final response =
        await http.post(Uri.parse('$baseUrl/v1/cameras/$cameraId/livestart'));

    if (response.statusCode != 200) {
      throw Exception('Failed to start live stream');
    }
  }

  Future<String> getLiveStreamUrl(String cameraId) async {
    final url = '$baseUrl/v1/cameras/$cameraId/live';
    return url;
  }

  Future<void> stopLiveStream(String cameraId) async {
    final response =
        await http.post(Uri.parse('$baseUrl/v1/cameras/$cameraId/livestop'));

    if (response.statusCode != 200) {
      throw Exception('Failed to stop live stream');
    }
  }
}
