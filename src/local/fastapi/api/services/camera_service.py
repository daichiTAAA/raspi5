import base64
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
from sqlalchemy.ext.asyncio import AsyncSession

import api.models as models
import api.schemas as schemas
import api.cruds as cruds
from api.setup_logger import setup_logger

logger, log_decorator = setup_logger(__name__)


class CameraService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.cameras = {}
            logger.info("CameraService instance created")
            # 実行中のFFmpegプロセスを停止する
            logger.info("Stopping FFmpeg processes")
            cls._instance.stop_ffmpeg_processes()
        return cls._instance

    def create_camera_instance(self, camera_id: str, rtsp_url: str):
        logger.info(
            f"api.services.camera_service.add_camera: camera_id: {camera_id}, rtsp_url: {rtsp_url}"
        )
        if camera_id in self.cameras:
            logger.error(f"Camera already exists: {camera_id}")
            raise HTTPException(status_code=400, detail="Camera already exists")
        jpeg_dir_path = f"data/jpeg/{camera_id}"
        jpeg_fps = 1
        try:
            self.cameras[camera_id] = models.CameraInstance(
                camera_id=camera_id,
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
            logger.info(f"Camera {camera_id} added successfully")
        except Exception as e:
            logger.error(f"Error adding camera {camera_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_camera_instances(self):
        logger.info("api.services.camera_service.get_cameras")
        infos: dict[str, models.CameraInstance] = {}
        for camera_id, camera in self.cameras.items():
            hls_process_status = None
            jpeg_extract_process_status = None
            jpeg_stream_process_status = None
            cap_status = None
            if camera.hls_process is not None:
                hls_process_status = "hls file creating"
            if camera.jpeg_extract_process is not None:
                jpeg_extract_process_status = "jpeg file extracting"
            if camera.jpeg_stream_process is not None:
                jpeg_stream_process_status = "jpeg stream running"
            if camera.cap is not None:
                cap_status = "cap exists"

            info: models.CameraInstance = models.CameraInstance(
                camera_id=camera.camera_id,
                rtsp_url=camera.rtsp_url,
                hls_process=hls_process_status,
                jpeg_extract_process=jpeg_extract_process_status,
                jpeg_stream_process=jpeg_stream_process_status,
                cap=cap_status,
                m3u8_file_path=camera.m3u8_file_path,
                jpeg_dir_path=camera.jpeg_dir_path,
                hls_last_access_time=camera.hls_last_access_time,
                jpeg_fps=camera.jpeg_fps,
                jpeg_last_access_time=camera.jpeg_last_access_time,
                jpeg_stream_last_access_time=camera.jpeg_stream_last_access_time,
            )
            infos[camera_id] = info
        return infos

    def get_camera_instance_by_camera_id(self, camera_id: str):
        logger.info(
            f"api.services.camera_service.get_camera_instance_by_camera_id: camera_id: {camera_id}"
        )
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        camera: models.CameraInstance = self.cameras[camera_id]
        hls_process_status = None
        jpeg_extract_process_status = None
        jpeg_stream_process_status = None
        cap_status = None
        if camera.hls_process is not None:
            hls_process_status = "hls file creating"
        if camera.jpeg_extract_process is not None:
            jpeg_extract_process_status = "jpeg file extracting"
        if camera.jpeg_stream_process is not None:
            jpeg_stream_process_status = "jpeg stream running"
        if camera.cap is not None:
            cap_status = "cap exists"

        info: models.CameraInstance = models.CameraInstance(
            camera_id=camera.camera_id,
            rtsp_url=camera.rtsp_url,
            hls_process=hls_process_status,
            jpeg_extract_process=jpeg_extract_process_status,
            jpeg_stream_process=jpeg_stream_process_status,
            cap=cap_status,
            m3u8_file_path=camera.m3u8_file_path,
            jpeg_dir_path=camera.jpeg_dir_path,
            hls_last_access_time=camera.hls_last_access_time,
            jpeg_fps=camera.jpeg_fps,
            jpeg_last_access_time=camera.jpeg_last_access_time,
            jpeg_stream_last_access_time=camera.jpeg_stream_last_access_time,
        )
        return info

    def delete_camera_instance(self, camera_id: str):
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        camera: models.CameraInstance = self.cameras[camera_id]
        if camera.hls_process is not None:
            logger.info(f"Stopping stream for camera {camera_id}")
            try:
                logger.info(f"Stopping stream for camera {camera_id}")
                self.stop_hls_stream(camera_id)
                logger.info(f"Stream stopped for camera {camera_id}")
            except Exception as e:
                logger.error(f"Error stopping stream for camera {camera_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        if camera.jpeg_extract_process is not None:
            logger.info(f"Stopping jpeg process for camera {camera_id}")
            try:
                logger.info(f"Stopping jpeg process for camera {camera_id}")
                self.stop_jpeg_extract_process(camera_id)
                logger.info(f"Jpeg process stopped for camera {camera_id}")
            except Exception as e:
                logger.error(f"Error stopping jpeg process for camera {camera_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        if camera.jpeg_stream_process is not None:
            logger.info(f"Stopping jpeg stream for camera {camera_id}")
            try:
                logger.info(f"Stopping jpeg stream for camera {camera_id}")
                self.stop_jpeg_stream(camera_id)
                logger.info(f"Jpeg stream stopped for camera {camera_id}")
            except Exception as e:
                logger.error(f"Error stopping jpeg stream for camera {camera_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        try:
            del self.cameras[camera_id]
            logger.info(f"Camera {camera_id} removed successfully")
        except Exception as e:
            logger.error(f"Error removing camera {camera_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def stop_ffmpeg_processes(self):
        """実行中のFFmpegプロセスを停止する"""
        for proc in psutil.process_iter(["name", "cmdline"]):
            try:
                if "ffmpeg" in proc.info["name"]:
                    cmdline = " ".join(proc.info["cmdline"])
                    if "camera_" in cmdline and ".m3u8" in cmdline:
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

    def get_hls_files(self, camera_id: str):
        try:
            output_dir = os.path.abspath(f"static/{camera_id}")
            files = []
            for file in os.listdir(output_dir):
                if file.endswith(".ts") or file.endswith(".m3u8"):
                    files.append(file)
            logger.info(f"Hls files found for camera {camera_id}")
            return {"files": files}
        except Exception as e:
            logger.error(f"Error getting hls files for camera {camera_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def remove_hls_files(self, camera_id: str):
        try:
            output_dir = os.path.abspath(f"static/{camera_id}")
            if len(os.listdir(output_dir)) == 0:
                logger.info(f"No hls files found for camera {camera_id}")
                raise HTTPException(status_code=404, detail="No hls files found")
            if not os.path.exists(output_dir):
                logger.info(f"No hls files found for camera {camera_id}")
                raise HTTPException(status_code=404, detail="No hls files found")
            for file in os.listdir(output_dir):
                if file.endswith(".ts") or file.endswith(".m3u8"):
                    os.remove(os.path.join(output_dir, file))
            logger.info(f"Hls files removed for camera {camera_id}")
            return {"message": f"Hls files removed for camera {camera_id}"}
        except HTTPException as e:
            if e.status_code == 404:
                logger.warning(
                    f"Warnig error removing hls files {camera_id} but ignore it: {e}"
                )
                raise HTTPException(status_code=404, detail="No hls files found")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"Error removing hls files for camera {camera_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def start_hls_stream(self, camera_id: str, timeout: int):
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        camera: models.CameraInstance = self.cameras[camera_id]

        if camera.hls_process is not None:
            logger.error(f"Camera is already streaming: {camera_id}")
            raise HTTPException(status_code=400, detail="Camera is already streaming")

        m3u8_file_path = f"static/{camera_id}/camera_{camera_id}.m3u8"
        camera.m3u8_file_path = m3u8_file_path
        self.remove_hls_files(camera_id)

        output_dir = os.path.abspath(f"static/{camera_id}")
        os.makedirs(output_dir, exist_ok=True)

        try:
            logger.info(f"Starting stream for camera {camera_id}")
            process = (
                ffmpeg.input(camera.rtsp_url, rtsp_transport="tcp")
                .output(
                    os.path.join(output_dir, f"camera_{camera_id}.m3u8"),
                    format="hls",
                    hls_time=1,
                    hls_list_size=0,
                    hls_segment_filename=os.path.join(
                        output_dir, f"camera_{camera_id}_%Y%m%d_%H%M%S.ts"
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
            camera.hls_process = process

            # .m3u8ファイルの作成を待機するバックグラウンドタスクを開始
            logger.info(
                f"Starting background task to wait for m3u8 file for camera {camera_id}"
            )
            self.wait_for_m3u8_file(camera_id, m3u8_file_path)
            logger.info(f"m3u8 file created for camera {camera_id}")
            logger.info(f"Stream started for camera {camera_id}")
            # タイムアウト後にストリームを停止するバックグラウンドタスクを開始
            # 別スレッドで非同期実行する
            executor = concurrent.futures.ThreadPoolExecutor()
            executor.submit(self.stop_hls_stream_after_timeout, camera_id, timeout)
        except Exception as e:
            logger.error(f"Error starting stream for camera {camera_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def wait_for_m3u8_file(self, camera_id: str, m3u8_file_path: str):
        logger.info(
            f"api.services.camera_service.wait_for_m3u8_file: camera_id: {camera_id}"
        )
        i: int = 0
        while not os.path.exists(m3u8_file_path):
            time.sleep(1)
            i += 1
            if i > 120:
                logger.error(f"Timeout waiting for m3u8 file for camera {camera_id}")
                self.stop_hls_stream(camera_id)
                raise HTTPException(
                    status_code=500, detail="Timeout waiting for m3u8 file"
                )
        logger.info(f"m3u8 file created for camera {camera_id}")

    def get_hls_stream_url(self, camera_id: str):
        logger.info("api.services.camera_service.get_stream")
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        camera: models.CameraInstance = self.cameras[camera_id]
        if camera.hls_process is None:
            logger.error(f"Camera is not streaming: {camera_id}")
            raise HTTPException(status_code=400, detail="Camera is not streaming")

        logger.info(f"api.services.camera_service.get_stream: camera_id: {camera_id}")
        return {
            "camera_id": camera_id,
            "url": camera.m3u8_file_path,
        }

    def stop_hls_stream_after_timeout(self, camera_id: str, timeout: int):
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        camera: models.CameraInstance = self.cameras[camera_id]

        camera.hls_last_access_time = time.time()

        # 最終アクセス時間が指定した時間よりも古い場合はストリームを停止する
        while True:
            if time.time() - camera.hls_last_access_time > timeout:
                self.stop_hls_stream(camera_id)
                break
            time.sleep(1)

    def keep_hls_stream(self, camera_id: str):
        logger.info("api.services.camera_service.keep_hls_stream")
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        camera: models.CameraInstance = self.cameras[camera_id]

        # 最終アクセス時間を更新
        camera.hls_last_access_time = time.time()
        logger.info(f"Stream kept for camera {camera_id}")

    def stop_hls_stream(self, camera_id: str):
        if camera_id not in self.cameras:
            raise HTTPException(status_code=404, detail="Camera not found")

        camera: models.CameraInstance = self.cameras[camera_id]
        if camera.hls_process:
            try:
                # SIGTERMシグナルを送信してffmpegプロセスを終了
                camera.hls_process.send_signal(signal.SIGTERM)

                # プロセスの終了を待機（タイムアウト10秒）
                try:
                    camera.hls_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # タイムアウト後もプロセスが終了しない場合はSIGKILLを送信
                    camera.hls_process.send_signal(signal.SIGKILL)

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                camera.hls_process = None

    def start_rtsp_stream(self, camera_id: str):
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        camera: models.CameraInstance = self.cameras[camera_id]

        if camera.cap is not None:
            logger.error(f"Camera is already rtsp streaming: {camera_id}")
            raise HTTPException(
                status_code=400, detail="Camera is already rtsp streaming"
            )

        try:
            logger.info(f"Starting rtsp stream for camera {camera_id}")
            # OpenCVを使用してRTSPストリームから画像を取得する
            cap = cv2.VideoCapture(camera.rtsp_url)
            success, frame = cap.read()
            if not success:
                logger.error(f"Failed to start rtsp stream for camera {camera_id}")
                raise HTTPException(
                    status_code=400, detail="Failed to start rtsp stream"
                )
            camera.cap = cap
            logger.info(f"Live stream started for camera {camera_id}")
        except Exception as e:
            logger.error(f"Error starting rtsp stream for camera {camera_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_rtsp_stream(self, camera_id: str):
        logger.info("api.services.camera_service.get_rtsp_stream")
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        try:
            camera: models.CameraInstance = self.cameras[camera_id]
        except Exception as e:
            logger.error(f"Error getting camera {camera_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        if camera.cap is None:
            logger.error(f"Camera is not rtsp streaming: {camera_id}")
            raise HTTPException(status_code=400, detail="Camera is not rtsp streaming")

        logger.info(
            f"api.services.camera_service.get_rtsp_stream: camera_id: {camera_id}"
        )

        # RTSPストリームから画像を取得するジェネレーター関数
        cap = camera.cap
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

    async def stop_rtsp_stream(self, camera_id: str):
        if camera_id not in self.cameras:
            raise HTTPException(status_code=404, detail="Camera not found")

        camera: models.CameraInstance = self.cameras[camera_id]
        if camera.cap:
            try:
                # OpenCVのVideoCaptureを解放
                camera.cap.release()
                logger.info(f"Live stream stopped for camera {camera_id}")
            except Exception as e:
                logger.error(f"Error stopping rtsp stream for camera {camera_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                camera.cap = None

    def start_jpeg_extract_process(self, camera_id: str, timeout: int):
        """ffmpeg-pythonを使用してRTSPストリームからJPEG画像を取得し、画像の右上に日時を記載するプロセスを開始する"""
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        camera: models.CameraInstance = self.cameras[camera_id]

        if camera.jpeg_extract_process is not None:
            logger.error(f"Camera is already extracting jpeg: {camera_id}")
            raise HTTPException(
                status_code=400, detail="Camera is already extracting jpeg"
            )

        jpeg_dir_path = camera.jpeg_dir_path
        jpeg_fps = camera.jpeg_fps

        os.makedirs(jpeg_dir_path, exist_ok=True)

        try:
            logger.info(f"Starting jpeg process for camera {camera_id}")
            process = (
                ffmpeg.input(camera.rtsp_url, rtsp_transport="tcp")
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
            camera.jpeg_extract_process = process
            logger.info(f"Jpeg process started for camera {camera_id}")
            # タイムアウト後にストリームを停止するバックグラウンドタスクを開始
            # 別スレッドで非同期実行する
            executor = concurrent.futures.ThreadPoolExecutor()
            executor.submit(
                self.stop_jpeg_extract_process_after_timeout, camera_id, timeout
            )
        except Exception as e:
            logger.error(f"Error starting jpeg process for camera {camera_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def stop_jpeg_extract_process(self, camera_id: str):
        """ffmpegプロセスを停止する"""
        if camera_id not in self.cameras:
            raise HTTPException(status_code=404, detail="Camera not found")

        camera: models.CameraInstance = self.cameras[camera_id]
        if camera.jpeg_extract_process:
            try:
                # SIGTERMシグナルを送信してffmpegプロセスを終了
                camera.jpeg_extract_process.send_signal(signal.SIGTERM)

                # プロセスの終了を待機（タイムアウト10秒）
                try:
                    camera.jpeg_extract_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # タイムアウト後もプロセスが終了しない場合はSIGKILLを送信
                    camera.jpeg_extract_process.send_signal(signal.SIGKILL)

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                camera.jpeg_extract_process = None

    def stop_jpeg_extract_process_after_timeout(self, camera_id: str, timeout: int):
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        camera: models.CameraInstance = self.cameras[camera_id]

        camera.jpeg_last_access_time = time.time()

        # 最終アクセス時間が指定した時間よりも古い場合はストリームを停止する
        while True:
            if time.time() - camera.jpeg_last_access_time > timeout:
                self.stop_jpeg_extract_process(camera_id)
                break
            time.sleep(1)

    def keep_jpeg_extract_process(self, camera_id: str):
        logger.info("api.services.camera_service.keep_jpeg_extract_process")
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        camera: models.CameraInstance = self.cameras[camera_id]

        # 最終アクセス時間を更新
        camera.jpeg_last_access_time = time.time()
        logger.info(f"Jpeg process kept for camera {camera_id}")

    def generate_video_stream_from_jpeg(self, camera_id: str, timeout: int):
        logger.info("api.services.camera_service.generate_video_stream_from_jpeg")
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        camera: models.CameraInstance = self.cameras[camera_id]
        jpeg_dir_path = camera.jpeg_dir_path
        jpeg_fps = camera.jpeg_fps
        # frame_interval = 1.0 / jpeg_fps  # フレーム間隔を計算

        def stream():
            process = (
                ffmpeg.input(
                    f"{jpeg_dir_path}/*.jpg", pattern_type="glob", framerate=jpeg_fps
                )
                .output("pipe:1", format="mpegts", vcodec="libx264")
                .run_async(pipe_stdout=True, pipe_stderr=True)
            )
            camera.jpeg_stream_process = process
            while True:
                in_bytes = process.stdout.read(1024)
                if not in_bytes:
                    break
                yield in_bytes
                # time.sleep(frame_interval)

        # タイムアウト後にストリームを停止するバックグラウンドタスクを開始
        # 別スレッドで非同期実行する
        executor = concurrent.futures.ThreadPoolExecutor()
        executor.submit(self.stop_jpeg_stream_process_after_timeout, camera_id, timeout)

        return StreamingResponse(stream(), media_type="video/mp2t")

    def get_latest_jpeg(self, camera_id: str):
        logger.info("api.services.camera_service.get_latest_jpeg")
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        camera: models.CameraInstance = self.cameras[camera_id]
        jpeg_dir_path = camera.jpeg_dir_path
        jpeg_files = [f for f in os.listdir(jpeg_dir_path) if f.endswith(".jpg")]
        if not jpeg_files:
            logger.error(f"No jpeg files found for camera {camera_id}")
            raise HTTPException(status_code=404, detail="No jpeg files found")

        latest_jpeg = max(
            jpeg_files, key=lambda x: os.path.getctime(os.path.join(jpeg_dir_path, x))
        )
        latest_jpeg_path = os.path.join(jpeg_dir_path, latest_jpeg)

        with open(latest_jpeg_path, "rb") as file:
            image = Image.open(file)
            img_io = BytesIO()
            image.save(img_io, "JPEG")
            img_io.seek(0)

            return StreamingResponse(img_io, media_type="image/jpeg")

    def stop_jpeg_stream_process(self, camera_id: str):
        if camera_id not in self.cameras:
            raise HTTPException(status_code=404, detail="Camera not found")

        camera: models.CameraInstance = self.cameras[camera_id]
        if camera.jpeg_stream_process:
            try:
                # SIGTERMシグナルを送信してffmpegプロセスを終了
                camera.jpeg_stream_process.send_signal(signal.SIGTERM)

                # プロセスの終了を待機（タイムアウト10秒）
                try:
                    camera.jpeg_stream_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # タイムアウト後もプロセスが終了しない場合はSIGKILLを送信
                    camera.jpeg_stream_process.send_signal(signal.SIGKILL)

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                camera.jpeg_stream_process = None

    def stop_jpeg_stream_process_after_timeout(self, camera_id: str, timeout: int):
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        camera: models.CameraInstance = self.cameras[camera_id]

        camera.jpeg_stream_last_access_time = time.time()

        # 最終アクセス時間が指定した時間よりも古い場合はストリームを停止する
        while True:
            if time.time() - camera.jpeg_stream_last_access_time > timeout:
                self.stop_jpeg_stream_process(camera_id)
                break
            time.sleep(1)

    def keep_jpeg_stream_process(self, camera_id: str):
        logger.info("api.services.camera_service.keep_jpeg_stream")
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        camera: models.CameraInstance = self.cameras[camera_id]

        # 最終アクセス時間を更新
        camera.jpeg_stream_last_access_time = time.time()
        logger.info(f"Jpeg stream kept for camera {camera_id}")

    def remove_jpeg_files(self, camera_id: str):
        logger.info("api.services.camera_service.remove_jpeg_files")
        try:
            jpeg_dir_path = f"data/jpeg/{camera_id}"
            if len(os.listdir(jpeg_dir_path)) == 0:
                logger.info(f"No jpeg files found for camera {camera_id}")
                raise HTTPException(status_code=404, detail="No jpeg files found")
            if not os.path.exists(jpeg_dir_path):
                logger.info(f"No jpeg files found for camera {camera_id}")
                raise HTTPException(status_code=404, detail="No jpeg files found")
            for file in os.listdir(jpeg_dir_path):
                if file.endswith(".jpg"):
                    os.remove(os.path.join(jpeg_dir_path, file))
            logger.info(f"Jpeg files removed for camera {camera_id}")
            return {"message": f"Jpeg files removed for camera {camera_id}"}
        except HTTPException as e:
            if e.status_code == 404:
                logger.warning(
                    f"Warnig error removing jpeg files {camera_id} but ignore it: {e}"
                )
                raise HTTPException(status_code=404, detail="No jpeg files found")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"Error removing jpeg files for camera {camera_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def save_selected_area(
        self,
        db: AsyncSession,
        camera_id: str,
        saving_area: schemas.SaveArea,
    ):
        logger.info("api.services.camera_service.save_selected_area")
        try:
            camera_instance: models.CameraInstance = self.cameras[camera_id]
            area_selected_jpeg_dir_path = f"data/area_selected_jpeg/{camera_id}"
            os.makedirs(area_selected_jpeg_dir_path, exist_ok=True)
            area_selected_jpeg_path = os.path.join(
                area_selected_jpeg_dir_path, f"area_selected_{camera_id}.jpg"
            )

            # Base64デコード
            jpeg_data = base64.b64decode(saving_area.area_selected_jpeg_data)

            with open(area_selected_jpeg_path, "wb") as file:
                file.write(jpeg_data)
            updating_camera = schemas.CameraUpdate(
                camera_id=camera_id,
                rtsp_url=camera_instance.rtsp_url,
                area_selected_jpeg_path=area_selected_jpeg_path,
                area_selected_jpeg_width=saving_area.area_selected_jpeg_width,
                area_selected_jpeg_height=saving_area.area_selected_jpeg_height,
                selected_area_start_x=saving_area.selected_area_start_x,
                selected_area_start_y=saving_area.selected_area_start_y,
                selected_area_end_x=saving_area.selected_area_end_x,
                selected_area_end_y=saving_area.selected_area_end_y,
            )
            updated_camera = await cruds.camera.update_camera(
                db, camera_id, updating_camera
            )
            logger.info(f"Selected area saved for camera {camera_id}, {updated_camera}")
            return {
                "message": f"Selected area saved for camera {camera_id}, {updated_camera}"
            }
        except Exception as e:
            logger.error(f"Error saving selected area for camera {camera_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))


async def get_selected_area(
    db: AsyncSession,
    camera_id: str,
):
    logger.info("api.services.camera_service.get_selected_area")
    try:
        saved_camera: models.Camera = await cruds.camera.get_camera_by_camera_id(
            db, camera_id
        )
        if saved_camera.area_selected_jpeg_path is None:
            logger.error(f"No selected area found for camera {camera_id}")
            raise HTTPException(status_code=404, detail="No selected area found")
        jpeg_path = saved_camera.area_selected_jpeg_path
        img_io = BytesIO()
        # 画像をバイト列に変換
        with open(jpeg_path, "rb") as file:
            image = Image.open(file)
            image.save(img_io, "JPEG")
            img_io.seek(0)
        logger.info(f"Got selected area saved for camera {camera_id}, {saved_camera}")
        got_area = schemas.GetArea(
            area_selected_jpeg_data=base64.b64encode(img_io.read()).decode("utf-8"),
            area_selected_jpeg_width=saved_camera.area_selected_jpeg_width,
            area_selected_jpeg_height=saved_camera.area_selected_jpeg_height,
            selected_area_start_x=saved_camera.selected_area_start_x,
            selected_area_start_y=saved_camera.selected_area_start_y,
            selected_area_end_x=saved_camera.selected_area_end_x,
            selected_area_end_y=saved_camera.selected_area_end_y,
        )
        return got_area
    except HTTPException as e:
        if e.status_code == 404:
            logger.warning(
                f"Warnig error getting selected area {camera_id} but ignore it: {e}"
            )
            raise HTTPException(status_code=404, detail="No selected area found")
        raise HTTPException(status_code=500, detail=str(e))
