import sys
import time
from PIL import Image

sys.path.append("/usr/lib/python3/dist-packages")
print(sys.path)
import picamera2

# Picamera2の設定
camera = picamera2.Picamera2()
camera_config = camera.create_video_configuration()
camera.configure(camera_config)
width = camera_config["main"]["size"][0]
height = camera_config["main"]["size"][1]
pix_fmt = camera_config["main"]["format"]

# 画像保存先ディレクトリ
output_dir = "./images/"

# 画像保存間隔（秒）
save_interval = 1

# カメラの開始
camera.start()

try:
    last_save_time = time.time()
    frame_count = 0
    while True:
        frame = camera.capture_array()

        # 現在の時刻を取得
        current_time = time.time()

        # 指定した間隔で画像を保存
        if current_time - last_save_time >= save_interval:
            # 画像ファイル名を生成
            filename = f"{output_dir}frame_{frame_count:06d}.jpg"

            # NumPy配列をPIL画像に変換
            img = Image.fromarray(frame)

            # 画像をRGBモードに変換
            img = img.convert("RGB")

            # 画像を保存
            img.save(filename)

            last_save_time = current_time
            frame_count += 1

        # 少し待機してCPU負荷を軽減
        time.sleep(0.01)

finally:
    camera.stop()
