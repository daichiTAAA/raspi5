class SaveAreaRequest {
  final String areaSelectedJpegData;
  final String areaSelectedJpegWidth;
  final String areaSelectedJpegHeight;
  final String selectedAreaStartX;
  final String selectedAreaStartY;
  final String selectedAreaEndX;
  final String selectedAreaEndY;

  SaveAreaRequest({
    required this.areaSelectedJpegData,
    required this.areaSelectedJpegWidth,
    required this.areaSelectedJpegHeight,
    required this.selectedAreaStartX,
    required this.selectedAreaStartY,
    required this.selectedAreaEndX,
    required this.selectedAreaEndY,
  });

  Map<String, dynamic> toJson() {
    return {
      'area_selected_jpeg_data': areaSelectedJpegData,
      'area_selected_jpeg_width': areaSelectedJpegWidth,
      'area_selected_jpeg_height': areaSelectedJpegHeight,
      'selected_area_start_x': selectedAreaStartX,
      'selected_area_start_y': selectedAreaStartY,
      'selected_area_end_x': selectedAreaEndX,
      'selected_area_end_y': selectedAreaEndY,
    };
  }
}

class SaveAreaResponse {
  final String areaSelectedJpegData;
  final String areaSelectedJpegWidth;
  final String areaSelectedJpegHeight;
  final String selectedAreaStartX;
  final String selectedAreaStartY;
  final String selectedAreaEndX;
  final String selectedAreaEndY;

  SaveAreaResponse({
    required this.areaSelectedJpegData,
    required this.areaSelectedJpegWidth,
    required this.areaSelectedJpegHeight,
    required this.selectedAreaStartX,
    required this.selectedAreaStartY,
    required this.selectedAreaEndX,
    required this.selectedAreaEndY,
  });

  factory SaveAreaResponse.fromJson(Map<String, dynamic> json) {
    return SaveAreaResponse(
      areaSelectedJpegWidth: json['area_selected_jpeg_width'],
      areaSelectedJpegHeight: json['area_selected_jpeg_height'],
      areaSelectedJpegData: json['area_selected_jpeg_data'],
      selectedAreaStartX: json['selected_area_start_x'],
      selectedAreaStartY: json['selected_area_start_y'],
      selectedAreaEndX: json['selected_area_end_x'],
      selectedAreaEndY: json['selected_area_end_y'],
    );
  }
}
