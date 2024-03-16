import sys
import time

sys.path.append("/usr/lib/python3/dist-packages")
print(sys.path)

import cv2
import picamera2
from picamera2 import YUV420_to_RGB
import ffmpeg
from libcamera import controls

# Picamera2の設定
camera = picamera2.Picamera2()
camera_config = camera.create_video_configuration(
    main={"format": "YUV420"},
    controls={
        "AfMode": controls.AfModeEnum.Continuous,
        "AfSpeed": controls.AfSpeedEnum.Fast,
        "AwbEnable": True,
    },
)
camera.configure(camera_config)

size = camera_config["main"]["size"]
width, height = size
fps = 30

# FFmpegの設定
output_url = "rtsp://0.0.0.0:8554/stream"
output_args = {
    "vcodec": "h264",
    "pix_fmt": "yuv420p",
    "video_bitrate": "4000k",
    "tune": "zerolatency",
    "preset": "veryfast",
    "f": "rtsp",
    "rtsp_transport": "tcp",
    "r": fps,
}

# RTSPストリームを開始
process = (
    ffmpeg.input(
        "pipe:",
        format="rawvideo",
        pix_fmt="rgb24",
        s="{}x{}".format(width, height),
        r=fps,
    )
    .output(output_url, **output_args)
    .overwrite_output()
    .run_async(pipe_stdin=True)
)

# カメラの開始
camera.start()

try:
    while True:
        frame = camera.capture_array()
        rgb = cv2.cvtColor(frame, cv2.COLOR_YUV420p2BGR)
        process.stdin.write(rgb.tobytes())
        # 少し待機してCPU負荷を軽減
        time.sleep(1 / fps)

finally:
    camera.stop()
    process.stdin.close()
    process.wait()
