"""ビデオストリームを受信しローカルフォルダに保存する"""

import ffmpeg
import os
import concurrent.futures

# IPアドレス
ip_address = "192.168.0.3"

# RTSP URL
rtsp_url1 = f"rtsp://{ip_address}:8554/stream1"
rtsp_url2 = f"rtsp://{ip_address}:8554/stream2"

# 保存先フォルダ
output_folder1 = "output1"
output_folder2 = "output2"

# 切り出しfps
extract_fps = 1

# 保存先フォルダが存在しない場合は作成
os.makedirs(output_folder1, exist_ok=True)
os.makedirs(output_folder2, exist_ok=True)


def process_stream(rtsp_url, output_folder):
    # 画像切り出しと保存
    (
        ffmpeg.input(rtsp_url)
        .filter("fps", fps=extract_fps)
        .output(
            f"{output_folder}/{ip_address}_%Y%m%d_%H%M%S_fps{extract_fps}.jpg",
            format="image2",
            strftime=1,
            qscale=1,
            preset="veryslow",
            crf=0,
        )
        .run(capture_stdout=True, capture_stderr=True)
    )


# マルチスレッドで並列処理
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [
        executor.submit(process_stream, rtsp_url1, output_folder1),
        executor.submit(process_stream, rtsp_url2, output_folder2),
    ]

    # すべての処理が完了するまで待機
    concurrent.futures.wait(futures)
