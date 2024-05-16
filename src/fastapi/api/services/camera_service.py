import asyncio
import os
import signal
import time
import subprocess
import concurrent.futures


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

    def add_camera(self, camera_id: str, rtsp_url: str):
        logger.info(
            f"api.services.camera_service.add_camera: camera_id: {camera_id}, rtsp_url: {rtsp_url}"
        )
        if camera_id in self.cameras:
            logger.error(f"Camera already exists: {camera_id}")
            raise HTTPException(status_code=400, detail="Camera already exists")
        try:
            self.cameras[camera_id] = Camera(
                id=camera_id,
                rtsp_url=rtsp_url,
                process=None,
                cap=None,
                m3u8_file_path=None,
                last_access_time=None,
            )
            logger.info(f"Camera {camera_id} added successfully")
        except Exception as e:
            logger.error(f"Error adding camera {camera_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def remove_hls_files(self, camera_id: str):
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        camera: Camera = self.cameras[camera_id]

        if camera.m3u8_file_path is None:
            logger.warning(f"m3u8 file not found for camera {camera_id}")
            return {
                "message": f"m3u8 file path is not registered for camera {camera_id}"
            }

        # m3u8ファイルがない場合は警告を返す
        if not os.path.exists(camera.m3u8_file_path):
            logger.warning(f"m3u8 file not found for camera {camera_id}")
            return {"message": f"m3u8 file not found for camera {camera_id}"}

        try:
            output_dir = os.path.abspath(f"static/{camera_id}")
            for file in os.listdir(output_dir):
                if file.endswith(".ts") or file.endswith(".m3u8"):
                    os.remove(os.path.join(output_dir, file))
            logger.info(f"Hls files removed for camera {camera_id}")
            return {"message": f"Hls files removed for camera {camera_id}"}
        except Exception as e:
            logger.error(f"Error removing hls files for camera {camera_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def start_hls_stream(self, camera_id: str, timeout: int):
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        camera: Camera = self.cameras[camera_id]

        if camera.process is not None:
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
                    hls_time=2,
                    hls_list_size=10,
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
            camera.process = process

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

        camera: Camera = self.cameras[camera_id]
        if camera.process is None:
            logger.error(f"Camera is not streaming: {camera_id}")
            raise HTTPException(status_code=400, detail="Camera is not streaming")

        logger.info(f"api.services.camera_service.get_stream: camera_id: {camera_id}")
        return {
            "camera_id": camera_id,
            "url": camera.m3u8_file_path,
        }

    # def get_hls_stream(self, camera_id: str, timeout: int):
    #     if camera_id not in self.cameras:
    #         logger.error(f"Camera not found: {camera_id}")
    #         raise HTTPException(status_code=404, detail="Camera not found")

    #     camera: Camera = self.cameras[camera_id]

    #     # 最終アクセス時間を更新
    #     camera.last_access_time = time.time()

    #     file_like = open(camera.m3u8_file_path, mode="rb")

    #     # 一定時間アクセスがない場合にffmpegプロセスを終了する処理を追加
    #     self.stop_hls_stream_after_timeout(
    #         camera_id, camera.last_access_time, timeout
    #     )

    #     return StreamingResponse(file_like, media_type="application/x-mpegURL")

    def stop_hls_stream_after_timeout(self, camera_id: str, timeout: int):
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        camera: Camera = self.cameras[camera_id]

        camera.last_access_time = time.time()

        # 最終アクセス時間が指定した時間よりも古い場合はストリームを停止する
        while True:
            if time.time() - camera.last_access_time > timeout:
                self.stop_hls_stream(camera_id)
                break
            time.sleep(1)

    def keep_hls_stream(self, camera_id: str):
        logger.info("api.services.camera_service.keep_hls_stream")
        if camera_id not in self.cameras:
            logger.error(f"Camera not found: {camera_id}")
            raise HTTPException(status_code=404, detail="Camera not found")

        camera: Camera = self.cameras[camera_id]

        # 最終アクセス時間を更新
        camera.last_access_time = time.time()
        logger.info(f"Stream kept for camera {camera_id}")

    def stop_hls_stream(self, camera_id: str):
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
                self.stop_hls_stream(camera_id)
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
