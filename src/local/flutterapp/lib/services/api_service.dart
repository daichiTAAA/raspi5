import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:sync_http/sync_http.dart';
import 'package:logger/logger.dart';

import '../models/save_area.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8100';
  var logger = Logger();

  // Future<void> addCamera(String cameraId, String rtspUrl) async {
  //   final response = await http.post(
  //     Uri.parse('$baseUrl/v1/cameras'),
  //     headers: <String, String>{
  //       'Content-Type': 'application/json; charset=UTF-8',
  //     },
  //     body: jsonEncode(<String, String>{
  //       'camera_id': cameraId,
  //       'rtsp_url': rtspUrl,
  //     }),
  //   );

  //   if (response.statusCode != 200) {
  //     throw Exception('Failed to add camera');
  //   }
  // }

  void addCamera(String cameraId, String rtspUrl) {
    final request = SyncHttpClient.postUrl(
        Uri.parse('$baseUrl/v1/camerainstances/$cameraId'));
    request.headers.set('Content-Type', 'application/json; charset=UTF-8');
    request.write(jsonEncode(<String, String>{
      'camera_id': cameraId,
      'rtsp_url': rtspUrl,
    }));
    final response = request.close();

    if (response.statusCode == 400 &&
        response.body == '{"detail":"Camera already exists"}') {
      return;
    }

    if (response.statusCode != 200) {
      throw Exception('Failed to add camera');
    }
  }

  // Future<void> startHlsStream(String cameraId) async {
  //   final response =
  //       await http.post(Uri.parse('$baseUrl/v1/cameras/$cameraId/hlsstart'));

  //   if (response.statusCode != 200) {
  //     throw Exception('Failed to start stream');
  //   }
  // }
  void startHlsStream(String cameraId) {
    final request =
        SyncHttpClient.postUrl(Uri.parse('$baseUrl/v1/hlss/$cameraId/start'));
    request.headers.set('Content-Type', 'application/json; charset=UTF-8');
    request.write(jsonEncode(<String, String>{
      'camera_id': cameraId,
    }));
    final response = request.close();

    if (response.statusCode != 200) {
      throw Exception('Failed to start stream');
    }
  }

  // Future<HlsStream> getStream(String cameraId) async {
  //   final response =
  //       await http.get(Uri.parse('$baseUrl/v1/cameras/$cameraId/stream'));

  //   if (response.statusCode == 200) {
  //     final jsonResponse = json.decode(response.body);
  //     return HlsStream.fromJson(jsonResponse);
  //   } else {
  //     throw Exception('Failed to get hls m3u8 url');
  //   }
  // }

  String getHlsStreamUrl(String cameraId) {
    final url = Uri.parse('$baseUrl/v1/hlss/$cameraId/url');
    final request = SyncHttpClient.getUrl(url);
    request.headers.set('Content-Type', 'application/json; charset=UTF-8');

    final response = request.close();

    if (response.statusCode != 200) {
      throw Exception('Failed to get hls m3u8 url');
    }

    final jsonResponse = json.decode(response.body.toString());
    final hlsUrl = jsonResponse['url'];
    return 'http://localhost:8100/$hlsUrl';
  }

  // String getHlsStreamUrl(String cameraId) {
  //   final url = '$baseUrl/v1/cameras/$cameraId/hlsurl';
  //   return url;
  // }

  // Future<void> stopStream(String cameraId) async {
  //   final response =
  //       await http.post(Uri.parse('$baseUrl/v1/cameras/$cameraId/stop'));

  //   if (response.statusCode != 200) {
  //     throw Exception('Failed to stop stream');
  //   }
  // }

  void keepHlsStreamAlive(String cameraId) {
    final request = SyncHttpClient.postUrl(
        Uri.parse('$baseUrl/v1/hlss/$cameraId/keepalive'));
    request.headers.set('Content-Type', 'application/json; charset=UTF-8');
    request.write(jsonEncode(<String, String>{
      'camera_id': cameraId,
    }));
    final response = request.close();

    if (response.statusCode != 200) {
      throw Exception('Failed to keep stream alive');
    }
  }

  void stopHlsStream(String cameraId) {
    final request =
        SyncHttpClient.postUrl(Uri.parse('$baseUrl/v1/hlss/$cameraId/stop'));
    request.headers.set('Content-Type', 'application/json; charset=UTF-8');
    request.write(jsonEncode(<String, String>{
      'camera_id': cameraId,
    }));
    final response = request.close();

    if (response.statusCode != 200) {
      throw Exception('Failed to stop stream');
    }
  }

  Future<void> removeCamera(String cameraId) async {
    final response =
        await http.delete(Uri.parse('$baseUrl/v1/camerainstances/$cameraId'));

    if (response.statusCode != 200) {
      throw Exception('Failed to remove camera');
    }
  }

  Future<void> startLiveStream(String cameraId) async {
    final response =
        await http.post(Uri.parse('$baseUrl/v1/rtsps/$cameraId/start'));

    if (response.statusCode != 200) {
      throw Exception('Failed to start live stream');
    }
  }

  Future<String> getLiveStreamUrl(String cameraId) async {
    final url = '$baseUrl/v1/rtsps/$cameraId';
    return url;
  }

  Future<void> stopLiveStream(String cameraId) async {
    final response =
        await http.post(Uri.parse('$baseUrl/v1/rtsps/$cameraId/stop'));

    if (response.statusCode != 200) {
      throw Exception('Failed to stop live stream');
    }
  }

  void startJpegExtractProcess(String cameraId) {
    final request =
        SyncHttpClient.postUrl(Uri.parse('$baseUrl/v1/jpegs/$cameraId/start'));
    request.headers.set('Content-Type', 'application/json; charset=UTF-8');
    final response = request.close();

    if (response.statusCode != 200) {
      throw Exception('Failed to start JPEG process');
    }
  }

  void stopJpegExtractProcess(String cameraId) {
    final request =
        SyncHttpClient.postUrl(Uri.parse('$baseUrl/v1/jpegs/$cameraId/stop'));
    request.headers.set('Content-Type', 'application/json; charset=UTF-8');
    final response = request.close();

    if (response.statusCode != 200) {
      throw Exception('Failed to stop JPEG process');
    }
  }

  void keepJpegExtractProcessAlive(String cameraId) {
    final request = SyncHttpClient.postUrl(
        Uri.parse('$baseUrl/v1/jpegs/$cameraId/keepalive'));
    request.headers.set('Content-Type', 'application/json; charset=UTF-8');
    final response = request.close();

    if (response.statusCode != 200) {
      throw Exception('Failed to keep JPEG process alive');
    }
  }

  String getJpegStreamUrl(String cameraId) {
    final url = Uri.parse('$baseUrl/v1/jpegs/$cameraId/stream');
    return url.toString();
  }

  void keepJpegStreamProcessAlive(String cameraId) {
    final request = SyncHttpClient.postUrl(
        Uri.parse('$baseUrl/v1/jpegs/$cameraId/keep_stream'));
    request.headers.set('Content-Type', 'application/json; charset=UTF-8');
    final response = request.close();

    if (response.statusCode != 200) {
      throw Exception('Failed to keep JPEG process alive');
    }
  }

  void stopJpegStreamProcess(String cameraId) {
    final request = SyncHttpClient.postUrl(
        Uri.parse('$baseUrl/v1/jpegs/$cameraId/stop_stream'));
    request.headers.set('Content-Type', 'application/json; charset=UTF-8');
    final response = request.close();

    if (response.statusCode != 200) {
      throw Exception('Failed to stop JPEG stream');
    }
  }

  Future<Uint8List> getLatestRecordedImage(String cameraId) async {
    final response =
        await http.get(Uri.parse('$baseUrl/v1/jpegs/$cameraId/latest_jpeg'));

    if (response.statusCode != 200) {
      logger.e('Failed to get latest recorded image');
      return Uint8List(0);
    }

    return response.bodyBytes;
  }

  void saveSelectedArea(
      String cameraId,
      Uint8List image,
      double originalWidth,
      double originalHeight,
      double originalStartX,
      double originalStartY,
      double originalEndX,
      double originalEndY) {
    final request = SyncHttpClient.postUrl(
        Uri.parse('$baseUrl/v1/jpegs/$cameraId/save_area'));
    request.headers.set('Content-Type', 'application/json; charset=UTF-8');

    // 画像をBase64エンコード
    String base64Image = base64Encode(image);

    // SaveAreaRequestオブジェクトを作成
    SaveAreaRequest saveAreaRequest = SaveAreaRequest(
      areaSelectedJpegData: base64Image,
      areaSelectedJpegWidth: originalWidth.toString(),
      areaSelectedJpegHeight: originalHeight.toString(),
      selectedAreaStartX: originalStartX.toString(),
      selectedAreaStartY: originalStartY.toString(),
      selectedAreaEndX: originalEndX.toString(),
      selectedAreaEndY: originalEndY.toString(),
    );

    // JSONに変換してリクエストに書き込む
    request.write(jsonEncode(saveAreaRequest.toJson()));
    final response = request.close();

    if (response.statusCode != 200) {
      throw Exception('Failed to save selected area');
    }
  }

  // 保存した範囲を取得する
  Future<SaveAreaResponse> getSelectedArea(String cameraId) async {
    final response =
        await http.get(Uri.parse('$baseUrl/v1/jpegs/$cameraId/area'));

    if (response.statusCode == 200) {
      final jsonResponse = json.decode(response.body);
      return SaveAreaResponse.fromJson(jsonResponse);
    } else if (response.statusCode == 404) {
      return SaveAreaResponse(
        areaSelectedJpegData: '',
        areaSelectedJpegWidth: '',
        areaSelectedJpegHeight: '',
        selectedAreaStartX: '',
        selectedAreaStartY: '',
        selectedAreaEndX: '',
        selectedAreaEndY: '',
      );
    } else {
      throw Exception('Failed to get selected area');
    }
  }
}
