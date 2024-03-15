import sys

sys.path.append("/usr/lib/python3/dist-packages")
print(sys.path)

from picamera2 import Picamera2, Preview

picam2 = Picamera2()
# 画像をプレビューしない設定をする
picam2.start_preview(Preview.NULL)

# カメラ画像を保存する
picam2.start_and_capture_file("test.jpg")
