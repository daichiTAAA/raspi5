import concurrent.futures
from io import BytesIO
import os
import signal
import subprocess
import time

import cv2
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
import ffmpeg
import psutil
from PIL import Image


import api.models as models
from api.setup_logger import setup_logger

logger, log_decorator = setup_logger(__name__)


class UserService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.users = {}
            logger.info("UserService instance created")
            # 実行中のFFmpegプロセスを停止する
            logger.info("Stopping FFmpeg processes")
            cls._instance.stop_ffmpeg_processes()
        return cls._instance

    def create_user_instance(self, user_id: str, rtsp_url: str):
        if user_id in self.users:
            logger.error(f"User already exists: {user_id}")
            raise HTTPException(status_code=400, detail="User already exists")
        jpeg_dir_path = f"data/jpeg/{user_id}"
        jpeg_fps = 1
        try:
            self.users[user_id] = models.UserInstance(
                user_id=user_id,
                rtsp_url=rtsp_url,
                hls_process=None,
                jpeg_extract_process=None,
                jpeg_stream_process=None,
                cap=None,
                m3u8_file_path=None,
                jpeg_dir_path=jpeg_dir_path,
                hls_last_access_time=None,
                jpeg_fps=jpeg_fps,
                jpeg_last_access_time=None,
                jpeg_stream_last_access_time=None,
            )
            logger.info(f"User {user_id} added successfully")
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_user_instances(self):
        logger.info("api.services.user_service.get_users")
        infos: dict[str, models.UserInstance] = {}
        for user_id, user in self.users.items():
            hls_process_status = None
            jpeg_extract_process_status = None
            jpeg_stream_process_status = None
            cap_status = None
            if user.hls_process is not None:
                hls_process_status = "hls file creating"
            if user.jpeg_extract_process is not None:
                jpeg_extract_process_status = "jpeg file extracting"
            if user.jpeg_stream_process is not None:
                jpeg_stream_process_status = "jpeg stream running"
            if user.cap is not None:
                cap_status = "cap exists"

            info: models.UserInstance = models.UserInstance(
                user_id=user.user_id,
                rtsp_url=user.rtsp_url,
                hls_process=hls_process_status,
                jpeg_extract_process=jpeg_extract_process_status,
                jpeg_stream_process=jpeg_stream_process_status,
                cap=cap_status,
                m3u8_file_path=user.m3u8_file_path,
                jpeg_dir_path=user.jpeg_dir_path,
                hls_last_access_time=user.hls_last_access_time,
                jpeg_fps=user.jpeg_fps,
                jpeg_last_access_time=user.jpeg_last_access_time,
                jpeg_stream_last_access_time=user.jpeg_stream_last_access_time,
            )
            infos[user_id] = info
        return infos

    def get_user_instance_by_user_id(self, user_id: str):
        logger.info(
            f"api.services.user_service.get_user_instance_by_user_id: user_id: {user_id}"
        )
        if user_id not in self.users:
            logger.error(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        user: models.UserInstance = self.users[user_id]
        hls_process_status = None
        jpeg_extract_process_status = None
        jpeg_stream_process_status = None
        cap_status = None
        if user.hls_process is not None:
            hls_process_status = "hls file creating"
        if user.jpeg_extract_process is not None:
            jpeg_extract_process_status = "jpeg file extracting"
        if user.jpeg_stream_process is not None:
            jpeg_stream_process_status = "jpeg stream running"
        if user.cap is not None:
            cap_status = "cap exists"

        info: models.UserInstance = models.UserInstance(
            user_id=user.user_id,
            rtsp_url=user.rtsp_url,
            hls_process=hls_process_status,
            jpeg_extract_process=jpeg_extract_process_status,
            jpeg_stream_process=jpeg_stream_process_status,
            cap=cap_status,
            m3u8_file_path=user.m3u8_file_path,
            jpeg_dir_path=user.jpeg_dir_path,
            hls_last_access_time=user.hls_last_access_time,
            jpeg_fps=user.jpeg_fps,
            jpeg_last_access_time=user.jpeg_last_access_time,
            jpeg_stream_last_access_time=user.jpeg_stream_last_access_time,
        )
        return info

    def delete_user_instance(self, user_id: str):
        if user_id not in self.users:
            logger.error(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        user: models.UserInstance = self.users[user_id]
        if user.hls_process is not None:
            logger.info(f"Stopping stream for user {user_id}")
            try:
                logger.info(f"Stopping stream for user {user_id}")
                self.stop_hls_stream(user_id)
                logger.info(f"Stream stopped for user {user_id}")
            except Exception as e:
                logger.error(f"Error stopping stream for user {user_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        if user.jpeg_extract_process is not None:
            logger.info(f"Stopping jpeg process for user {user_id}")
            try:
                logger.info(f"Stopping jpeg process for user {user_id}")
                self.stop_jpeg_extract_process(user_id)
                logger.info(f"Jpeg process stopped for user {user_id}")
            except Exception as e:
                logger.error(f"Error stopping jpeg process for user {user_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        if user.jpeg_stream_process is not None:
            logger.info(f"Stopping jpeg stream for user {user_id}")
            try:
                logger.info(f"Stopping jpeg stream for user {user_id}")
                self.stop_jpeg_stream(user_id)
                logger.info(f"Jpeg stream stopped for user {user_id}")
            except Exception as e:
                logger.error(f"Error stopping jpeg stream for user {user_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        try:
            del self.users[user_id]
            logger.info(f"User {user_id} removed successfully")
        except Exception as e:
            logger.error(f"Error removing user {user_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def stop_ffmpeg_processes(self):
        """実行中のFFmpegプロセスを停止する"""
        for proc in psutil.process_iter(["name", "cmdline"]):
            try:
                if "ffmpeg" in proc.info["name"]:
                    cmdline = " ".join(proc.info["cmdline"])
                    if "user_" in cmdline and ".m3u8" in cmdline:
                        # FFmpegプロセスを停止する
                        proc.terminate()
                        print(f"Terminated FFmpeg process: {cmdline}")
                        logger.info(f"Terminated FFmpeg process: {cmdline}")
            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ) as e:
                logger.error(f"Error stopping FFmpeg process: {e}")
                pass
            except Exception as e:
                logger.error(f"Error stopping FFmpeg process: {e}")
                pass

    def get_hls_files(self, user_id: str):
        try:
            output_dir = os.path.abspath(f"static/{user_id}")
            files = []
            for file in os.listdir(output_dir):
                if file.endswith(".ts") or file.endswith(".m3u8"):
                    files.append(file)
            logger.info(f"Hls files found for user {user_id}")
            return {"files": files}
        except Exception as e:
            logger.error(f"Error getting hls files for user {user_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def remove_hls_files(self, user_id: str):
        try:
            output_dir = os.path.abspath(f"static/{user_id}")
            if len(os.listdir(output_dir)) == 0:
                logger.info(f"No hls files found for user {user_id}")
                raise HTTPException(status_code=404, detail="No hls files found")
            if not os.path.exists(output_dir):
                logger.info(f"No hls files found for user {user_id}")
                raise HTTPException(status_code=404, detail="No hls files found")
            for file in os.listdir(output_dir):
                if file.endswith(".ts") or file.endswith(".m3u8"):
                    os.remove(os.path.join(output_dir, file))
            logger.info(f"Hls files removed for user {user_id}")
            return {"message": f"Hls files removed for user {user_id}"}
        except HTTPException as e:
            if e.status_code == 404:
                logger.warning(
                    f"Warnig error removing hls files {user_id} but ignore it: {e}"
                )
                raise HTTPException(status_code=404, detail="No hls files found")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"Error removing hls files for user {user_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def start_hls_stream(self, user_id: str, timeout: int):
        if user_id not in self.users:
            logger.error(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        user: models.UserInstance = self.users[user_id]

        if user.hls_process is not None:
            logger.error(f"User is already streaming: {user_id}")
            raise HTTPException(status_code=400, detail="User is already streaming")

        m3u8_file_path = f"static/{user_id}/user_{user_id}.m3u8"
        user.m3u8_file_path = m3u8_file_path
        self.remove_hls_files(user_id)

        output_dir = os.path.abspath(f"static/{user_id}")
        os.makedirs(output_dir, exist_ok=True)

        try:
            logger.info(f"Starting stream for user {user_id}")
            process = (
                ffmpeg.input(user.rtsp_url, rtsp_transport="tcp")
                .output(
                    os.path.join(output_dir, f"user_{user_id}.m3u8"),
                    format="hls",
                    hls_time=1,
                    hls_list_size=0,
                    hls_segment_filename=os.path.join(
                        output_dir, f"user_{user_id}_%Y%m%d_%H%M%S.ts"
                    ),
                    hls_segment_type="mpegts",
                    strftime=1,
                    vcodec="libx264",
                    acodec="aac",
                    g=30,
                    tune="zerolatency",
                )
                .global_args("-loglevel", "error")
                .run_async(pipe_stdin=True, pipe_stderr=True)
            )
            user.hls_process = process

            # .m3u8ファイルの作成を待機するバックグラウンドタスクを開始
            logger.info(
                f"Starting background task to wait for m3u8 file for user {user_id}"
            )
            self.wait_for_m3u8_file(user_id, m3u8_file_path)
            logger.info(f"m3u8 file created for user {user_id}")
            logger.info(f"Stream started for user {user_id}")
            # タイムアウト後にストリームを停止するバックグラウンドタスクを開始
            # 別スレッドで非同期実行する
            executor = concurrent.futures.ThreadPoolExecutor()
            executor.submit(self.stop_hls_stream_after_timeout, user_id, timeout)
        except Exception as e:
            logger.error(f"Error starting stream for user {user_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def wait_for_m3u8_file(self, user_id: str, m3u8_file_path: str):
        logger.info(f"api.services.user_service.wait_for_m3u8_file: user_id: {user_id}")
        i: int = 0
        while not os.path.exists(m3u8_file_path):
            time.sleep(1)
            i += 1
            if i > 120:
                logger.error(f"Timeout waiting for m3u8 file for user {user_id}")
                self.stop_hls_stream(user_id)
                raise HTTPException(
                    status_code=500, detail="Timeout waiting for m3u8 file"
                )
        logger.info(f"m3u8 file created for user {user_id}")

    def get_hls_stream_url(self, user_id: str):
        logger.info("api.services.user_service.get_stream")
        if user_id not in self.users:
            logger.error(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        user: models.UserInstance = self.users[user_id]
        if user.hls_process is None:
            logger.error(f"User is not streaming: {user_id}")
            raise HTTPException(status_code=400, detail="User is not streaming")

        logger.info(f"api.services.user_service.get_stream: user_id: {user_id}")
        return {
            "user_id": user_id,
            "url": user.m3u8_file_path,
        }

    def stop_hls_stream_after_timeout(self, user_id: str, timeout: int):
        if user_id not in self.users:
            logger.error(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        user: models.UserInstance = self.users[user_id]

        user.hls_last_access_time = time.time()

        # 最終アクセス時間が指定した時間よりも古い場合はストリームを停止する
        while True:
            if time.time() - user.hls_last_access_time > timeout:
                self.stop_hls_stream(user_id)
                break
            time.sleep(1)

    def keep_hls_stream(self, user_id: str):
        logger.info("api.services.user_service.keep_hls_stream")
        if user_id not in self.users:
            logger.error(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        user: models.UserInstance = self.users[user_id]

        # 最終アクセス時間を更新
        user.hls_last_access_time = time.time()
        logger.info(f"Stream kept for user {user_id}")

    def stop_hls_stream(self, user_id: str):
        if user_id not in self.users:
            raise HTTPException(status_code=404, detail="User not found")

        user: models.UserInstance = self.users[user_id]
        if user.hls_process:
            try:
                # SIGTERMシグナルを送信してffmpegプロセスを終了
                user.hls_process.send_signal(signal.SIGTERM)

                # プロセスの終了を待機（タイムアウト10秒）
                try:
                    user.hls_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # タイムアウト後もプロセスが終了しない場合はSIGKILLを送信
                    user.hls_process.send_signal(signal.SIGKILL)

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                user.hls_process = None

    def start_rtsp_stream(self, user_id: str):
        if user_id not in self.users:
            logger.error(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        user: models.UserInstance = self.users[user_id]

        if user.cap is not None:
            logger.error(f"User is already rtsp streaming: {user_id}")
            raise HTTPException(
                status_code=400, detail="User is already rtsp streaming"
            )

        try:
            logger.info(f"Starting rtsp stream for user {user_id}")
            # OpenCVを使用してRTSPストリームから画像を取得する
            cap = cv2.VideoCapture(user.rtsp_url)
            success, frame = cap.read()
            if not success:
                logger.error(f"Failed to start rtsp stream for user {user_id}")
                raise HTTPException(
                    status_code=400, detail="Failed to start rtsp stream"
                )
            user.cap = cap
            logger.info(f"Live stream started for user {user_id}")
        except Exception as e:
            logger.error(f"Error starting rtsp stream for user {user_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_rtsp_stream(self, user_id: str):
        logger.info("api.services.user_service.get_rtsp_stream")
        if user_id not in self.users:
            logger.error(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        try:
            user: models.UserInstance = self.users[user_id]
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        if user.cap is None:
            logger.error(f"User is not rtsp streaming: {user_id}")
            raise HTTPException(status_code=400, detail="User is not rtsp streaming")

        logger.info(f"api.services.user_service.get_rtsp_stream: user_id: {user_id}")

        # RTSPストリームから画像を取得するジェネレーター関数
        cap = user.cap
        while True:
            success, frame = cap.read()
            if not success:
                # raise HTTPException(status_code=400, detail="Failed to get frame")
                break
            # 画像をJPEG形式にエンコード
            ret, buffer = cv2.imencode(".jpg", frame)
            # メモリ上の画像データをバイト列に変換
            frame_bytes = buffer.tobytes()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )

    async def stop_rtsp_stream(self, user_id: str):
        if user_id not in self.users:
            raise HTTPException(status_code=404, detail="User not found")

        user: models.UserInstance = self.users[user_id]
        if user.cap:
            try:
                # OpenCVのVideoCaptureを解放
                user.cap.release()
                logger.info(f"Live stream stopped for user {user_id}")
            except Exception as e:
                logger.error(f"Error stopping rtsp stream for user {user_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                user.cap = None

    def start_jpeg_extract_process(self, user_id: str, timeout: int):
        """ffmpeg-pythonを使用してRTSPストリームからJPEG画像を取得し、画像の右上に日時を記載するプロセスを開始する"""
        if user_id not in self.users:
            logger.error(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        user: models.UserInstance = self.users[user_id]

        if user.jpeg_extract_process is not None:
            logger.error(f"User is already extracting jpeg: {user_id}")
            raise HTTPException(
                status_code=400, detail="User is already extracting jpeg"
            )

        jpeg_dir_path = user.jpeg_dir_path
        jpeg_fps = user.jpeg_fps

        os.makedirs(jpeg_dir_path, exist_ok=True)

        try:
            logger.info(f"Starting jpeg process for user {user_id}")
            process = (
                ffmpeg.input(user.rtsp_url, rtsp_transport="tcp")
                .output(
                    os.path.join(jpeg_dir_path, f"frame_%Y%m%d_%H%M%S.jpg"),
                    format="image2",
                    vcodec="mjpeg",
                    qscale=2,  # 最高画質
                    r=jpeg_fps,
                    strftime=1,
                    vf="drawtext=text='%{localtime}':x=w-tw-10:y=10:fontsize=24:fontcolor=white:box=1:boxcolor=black@0.5",
                    metadata="creation_time=now",
                )
                .global_args("-loglevel", "error")
                .run_async(pipe_stdout=True, pipe_stderr=True)
            )
            user.jpeg_extract_process = process
            logger.info(f"Jpeg process started for user {user_id}")
            # タイムアウト後にストリームを停止するバックグラウンドタスクを開始
            # 別スレッドで非同期実行する
            executor = concurrent.futures.ThreadPoolExecutor()
            executor.submit(
                self.stop_jpeg_extract_process_after_timeout, user_id, timeout
            )
        except Exception as e:
            logger.error(f"Error starting jpeg process for user {user_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def stop_jpeg_extract_process(self, user_id: str):
        """ffmpegプロセスを停止する"""
        if user_id not in self.users:
            raise HTTPException(status_code=404, detail="User not found")

        user: models.UserInstance = self.users[user_id]
        if user.jpeg_extract_process:
            try:
                # SIGTERMシグナルを送信してffmpegプロセスを終了
                user.jpeg_extract_process.send_signal(signal.SIGTERM)

                # プロセスの終了を待機（タイムアウト10秒）
                try:
                    user.jpeg_extract_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # タイムアウト後もプロセスが終了しない場合はSIGKILLを送信
                    user.jpeg_extract_process.send_signal(signal.SIGKILL)

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                user.jpeg_extract_process = None

    def stop_jpeg_extract_process_after_timeout(self, user_id: str, timeout: int):
        if user_id not in self.users:
            logger.error(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        user: models.UserInstance = self.users[user_id]

        user.jpeg_last_access_time = time.time()

        # 最終アクセス時間が指定した時間よりも古い場合はストリームを停止する
        while True:
            if time.time() - user.jpeg_last_access_time > timeout:
                self.stop_jpeg_extract_process(user_id)
                break
            time.sleep(1)

    def keep_jpeg_extract_process(self, user_id: str):
        logger.info("api.services.user_service.keep_jpeg_extract_process")
        if user_id not in self.users:
            logger.error(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        user: models.UserInstance = self.users[user_id]

        # 最終アクセス時間を更新
        user.jpeg_last_access_time = time.time()
        logger.info(f"Jpeg process kept for user {user_id}")

    def generate_video_stream_from_jpeg(self, user_id: str, timeout: int):
        logger.info("api.services.user_service.generate_video_stream_from_jpeg")
        if user_id not in self.users:
            logger.error(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        user: models.UserInstance = self.users[user_id]
        jpeg_dir_path = user.jpeg_dir_path
        jpeg_fps = user.jpeg_fps
        # frame_interval = 1.0 / jpeg_fps  # フレーム間隔を計算

        def stream():
            process = (
                ffmpeg.input(
                    f"{jpeg_dir_path}/*.jpg", pattern_type="glob", framerate=jpeg_fps
                )
                .output("pipe:1", format="mpegts", vcodec="libx264")
                .run_async(pipe_stdout=True, pipe_stderr=True)
            )
            user.jpeg_stream_process = process
            while True:
                in_bytes = process.stdout.read(1024)
                if not in_bytes:
                    break
                yield in_bytes
                # time.sleep(frame_interval)

        # タイムアウト後にストリームを停止するバックグラウンドタスクを開始
        # 別スレッドで非同期実行する
        executor = concurrent.futures.ThreadPoolExecutor()
        executor.submit(self.stop_jpeg_stream_process_after_timeout, user_id, timeout)

        return StreamingResponse(stream(), media_type="video/mp2t")

    def stop_jpeg_stream_process(self, user_id: str):
        if user_id not in self.users:
            raise HTTPException(status_code=404, detail="User not found")

        user: models.UserInstance = self.users[user_id]
        if user.jpeg_stream_process:
            try:
                # SIGTERMシグナルを送信してffmpegプロセスを終了
                user.jpeg_stream_process.send_signal(signal.SIGTERM)

                # プロセスの終了を待機（タイムアウト10秒）
                try:
                    user.jpeg_stream_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # タイムアウト後もプロセスが終了しない場合はSIGKILLを送信
                    user.jpeg_stream_process.send_signal(signal.SIGKILL)

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                user.jpeg_stream_process = None

    def stop_jpeg_stream_process_after_timeout(self, user_id: str, timeout: int):
        if user_id not in self.users:
            logger.error(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        user: models.UserInstance = self.users[user_id]

        user.jpeg_stream_last_access_time = time.time()

        # 最終アクセス時間が指定した時間よりも古い場合はストリームを停止する
        while True:
            if time.time() - user.jpeg_stream_last_access_time > timeout:
                self.stop_jpeg_stream_process(user_id)
                break
            time.sleep(1)

    def keep_jpeg_stream_process(self, user_id: str):
        logger.info("api.services.user_service.keep_jpeg_stream")
        if user_id not in self.users:
            logger.error(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        user: models.UserInstance = self.users[user_id]

        # 最終アクセス時間を更新
        user.jpeg_stream_last_access_time = time.time()
        logger.info(f"Jpeg stream kept for user {user_id}")

    def remove_jpeg_files(self, user_id: str):
        logger.info("api.services.user_service.remove_jpeg_files")
        try:
            jpeg_dir_path = f"data/jpeg/{user_id}"
            if len(os.listdir(jpeg_dir_path)) == 0:
                logger.info(f"No jpeg files found for user {user_id}")
                raise HTTPException(status_code=404, detail="No jpeg files found")
            if not os.path.exists(jpeg_dir_path):
                logger.info(f"No jpeg files found for user {user_id}")
                raise HTTPException(status_code=404, detail="No jpeg files found")
            for file in os.listdir(jpeg_dir_path):
                if file.endswith(".jpg"):
                    os.remove(os.path.join(jpeg_dir_path, file))
            logger.info(f"Jpeg files removed for user {user_id}")
            return {"message": f"Jpeg files removed for user {user_id}"}
        except HTTPException as e:
            if e.status_code == 404:
                logger.warning(
                    f"Warnig error removing jpeg files {user_id} but ignore it: {e}"
                )
                raise HTTPException(status_code=404, detail="No jpeg files found")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"Error removing jpeg files for user {user_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
