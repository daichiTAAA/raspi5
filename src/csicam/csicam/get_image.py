import sys

sys.path.append("/usr/lib/python3/dist-packages")
print(sys.path)

from picamera2 import Picamera2, Preview

picam2a = Picamera2(0)
picam2b = Picamera2(1)
picam2a.start_preview(Preview.NULL)
picam2b.start_preview(Preview.NULL)
# picam2a.start()
# picam2b.start()
picam2a.start_and_capture_file("cam0.jpg")
picam2b.start_and_capture_file("cam1.jpg")
# picam2a.capture_file("cam0.jpg")
# picam2b.capture_file("cam1.jpg")
# picam2a.stop()
# picam2b.stop()
