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
camera1 = picamera2.Picamera2(camera_num=0)
# camera2 = picamera2.Picamera2(camera_num=1)

camera_config1 = camera1.create_video_configuration(
    main={"format": "YUV420"},
    controls={
        "AfMode": controls.AfModeEnum.Continuous,
        "AfSpeed": controls.AfSpeedEnum.Fast,
        "AwbEnable": True,
    },
)
# camera_config2 = camera2.create_video_configuration(
#     main={"format": "YUV420"},
#     controls={
#         "AfMode": controls.AfModeEnum.Continuous,
#         "AfSpeed": controls.AfSpeedEnum.Fast,
#         "AwbEnable": True,
#     },
# )

camera1.configure(camera_config1)
# camera2.configure(camera_config2)

size = camera_config1["main"]["size"]
width, height = size
fps = 4

# FFmpegの設定
output_url1 = "rtsp://0.0.0.0:8554/stream1"
# output_url2 = "rtsp://0.0.0.0:8554/stream2"

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
process1 = (
    ffmpeg.input(
        "pipe:",
        format="rawvideo",
        pix_fmt="rgb24",
        s="{}x{}".format(width, height),
        r=fps,
    )
    .output(output_url1, **output_args)
    .overwrite_output()
    .run_async(pipe_stdin=True)
)

# process2 = (
#     ffmpeg.input(
#         "pipe:",
#         format="rawvideo",
#         pix_fmt="rgb24",
#         s="{}x{}".format(width, height),
#         r=fps,
#     )
#     .output(output_url2, **output_args)
#     .overwrite_output()
#     .run_async(pipe_stdin=True)
# )

# カメラの開始
camera1.start()
# camera2.start()

try:
    while True:
        frame1 = camera1.capture_array()
        # frame2 = camera2.capture_array()

        rgb1 = cv2.cvtColor(frame1, cv2.COLOR_YUV420p2BGR)
        # rgb2 = cv2.cvtColor(frame2, cv2.COLOR_YUV420p2BGR)

        process1.stdin.write(rgb1.tobytes())
        # process2.stdin.write(rgb2.tobytes())

        # 少し待機してCPU負荷を軽減
        time.sleep(1 / fps)

finally:
    camera1.stop()
    # camera2.stop()
    process1.stdin.close()
    # process2.stdin.close()
    process1.wait()
    # process2.wait()
