import asyncio
import os
import signal
import time
import subprocess
import json
from datetime import datetime, timedelta

import cv2
from fastapi import HTTPException, Depends
import ffmpeg
import psutil

from api.models.camera import Camera
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

    async def add_camera(self, camera_id: str, rtsp_url: str):
        logger.info(
            f"api.services.camera_service.add_camera: camera_id: {camera_id}, rtsp_url: {rtsp_url}"
        )
        if camera_id in self.cameras:
            logger.error(f"Camera already exists: {camera_id}")
            raise HTTPException(status_code=400, detail="Camera already exists")
        try:
            self.cameras[camera_id] = Camera(
                id=camera_id, rtsp_url=rtsp_url, process=None, cap=None
            )
            logger.info(f"Camera {camera_id} added successfully")
        except Exception as e:
            logger.error(f"Error adding camera {camera_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def start_stream(self, camera_id: str):
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        camera = self.cameras[camera_id]

        if camera.process is not None:
            logger.error(f"Camera is already streaming: {camera_id}")
            raise HTTPException(status_code=400, detail="Camera is already streaming")

        try:
            logger.info(f"Starting stream for camera {camera_id}")
            process = (
                ffmpeg.input(camera.rtsp_url, rtsp_transport="tcp")
                .output(
                    f"static/camera_{camera_id}.m3u8",
                    format="hls",
                    hls_time=20,
                    hls_list_size=10,
                    hls_segment_filename=f"static/camera_{camera_id}_%Y%m%d_%H%M%S.ts",
                    hls_segment_type="mpegts",
                    strftime=1,
                    vcodec="libx264",
                    acodec="aac",
                    g=30,
                    # bufsize="1M",
                    tune="zerolatency",
                )
                .global_args("-loglevel", "error")
                .run_async(pipe_stdin=True, pipe_stderr=True)
            )
            camera.process = process
            logger.info(f"Stream started for camera {camera_id}")

            # .m3u8ファイルの作成を待機するバックグラウンドタスクを開始
            logger.info(
                f"Starting background task to wait for m3u8 file for camera {camera_id}"
            )
            self.wait_for_m3u8_file(camera_id)
        except Exception as e:
            logger.error(f"Error starting stream for camera {camera_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def wait_for_m3u8_file(self, camera_id: str):
        logger.info(
            f"api.services.camera_service.wait_for_m3u8_file: camera_id: {camera_id}"
        )
        m3u8_file = f"static/camera_{camera_id}.m3u8"
        while not os.path.exists(m3u8_file):
            time.sleep(1)
        logger.info(f"m3u8 file created for camera {camera_id}")

    def get_stream(self, camera_id: str):
        logger.info("api.services.camera_service.get_stream")
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        camera = self.cameras[camera_id]
        if camera.process is None:
            logger.error(f"Camera is not streaming: {camera_id}")
            raise HTTPException(status_code=400, detail="Camera is not streaming")

        logger.info(f"api.services.camera_service.get_stream: camera_id: {camera_id}")
        return {
            "camera_id": camera_id,
            "url": f"http://localhost:8100/static/camera_{camera_id}.m3u8",
        }

    async def stop_stream(self, camera_id: str):
        if camera_id not in self.cameras:
            raise HTTPException(status_code=404, detail="Camera not found")

        camera = self.cameras[camera_id]
        if camera.process:
            try:
                # SIGTERMシグナルを送信してffmpegプロセスを終了
                camera.process.send_signal(signal.SIGTERM)

                # プロセスの終了を待機（タイムアウト10秒）
                try:
                    camera.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # タイムアウト後もプロセスが終了しない場合はSIGKILLを送信
                    camera.process.send_signal(signal.SIGKILL)

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                camera.process = None

    async def remove_camera(self, camera_id: str):
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        camera = self.cameras[camera_id]
        if camera.process is not None:
            logger.info(f"Stopping stream for camera {camera_id}")
            try:
                logger.info(f"Stopping stream for camera {camera_id}")
                await self.stop_stream(camera_id)
                logger.info(f"Stream stopped for camera {camera_id}")
            except Exception as e:
                logger.error(f"Error stopping stream for camera {camera_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        try:
            del self.cameras[camera_id]
            logger.info(f"Camera {camera_id} removed successfully")
        except Exception as e:
            logger.error(f"Error removing camera {camera_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def start_live_stream(self, camera_id: str):
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        camera = self.cameras[camera_id]

        if camera.cap is not None:
            logger.error(f"Camera is already live streaming: {camera_id}")
            raise HTTPException(
                status_code=400, detail="Camera is already live streaming"
            )

        try:
            logger.info(f"Starting live stream for camera {camera_id}")
            # OpenCVを使用してRTSPストリームから画像を取得する
            cap = cv2.VideoCapture(camera.rtsp_url)
            success, frame = cap.read()
            if not success:
                logger.error(f"Failed to start live stream for camera {camera_id}")
                raise HTTPException(
                    status_code=400, detail="Failed to start live stream"
                )
            camera.cap = cap
            logger.info(f"Live stream started for camera {camera_id}")
        except Exception as e:
            logger.error(f"Error starting live stream for camera {camera_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_live_stream(self, camera_id: str):
        logger.info("api.services.camera_service.get_live_stream")
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        try:
            camera = self.cameras[camera_id]
        except Exception as e:
            logger.error(f"Error getting camera {camera_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        if camera.cap is None:
            logger.error(f"Camera is not live streaming: {camera_id}")
            raise HTTPException(status_code=400, detail="Camera is not live streaming")

        logger.info(
            f"api.services.camera_service.get_live_stream: camera_id: {camera_id}"
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

    async def stop_live_stream(self, camera_id: str):
        if camera_id not in self.cameras:
            raise HTTPException(status_code=404, detail="Camera not found")

        camera = self.cameras[camera_id]
        if camera.cap:
            try:
                # OpenCVのVideoCaptureを解放
                camera.cap.release()
                logger.info(f"Live stream stopped for camera {camera_id}")
            except Exception as e:
                logger.error(f"Error stopping live stream for camera {camera_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                camera.cap = None
