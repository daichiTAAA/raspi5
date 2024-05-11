import io

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
import ffmpeg
import psutil

from api.models.camera import Camera
from api.setup_logger import setup_logger

logger, log_decorator = setup_logger(__name__)

app = FastAPI()


class CameraService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.cameras = {}
            # 実行中のFFmpegプロセスを停止する
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
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    async def add_camera(self, camera_id: str, rtsp_url: str):
        logger.info(
            f"api.services.camera_service.add_camera: camera_id: {camera_id}, rtsp_url: {rtsp_url}"
        )
        if camera_id in self.cameras:
            raise HTTPException(status_code=400, detail="Camera already exists")

        self.cameras[camera_id] = Camera(id=camera_id, rtsp_url=rtsp_url, process=None)

    async def start_stream(self, camera_id: str):
        if camera_id not in self.cameras:
            raise HTTPException(status_code=404, detail="Camera not found")

        camera = self.cameras[camera_id]

        if camera.process is not None:
            raise HTTPException(status_code=400, detail="Camera is already streaming")

        try:
            process = (
                ffmpeg.input(camera.rtsp_url, rtsp_transport="tcp")
                .output("pipe:1", format="mpegts")
                .global_args("-loglevel", "error")
                .run_async(pipe_stdout=True, pipe_stderr=True)
            )
            camera.process = process
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_stream(self, camera_id: str):
        logger.info("api.services.camera_service.get_stream")
        if camera_id not in self.cameras:
            raise HTTPException(status_code=404, detail="Camera not found")

        camera = self.cameras[camera_id]
        if camera.process is None:
            raise HTTPException(status_code=400, detail="Camera is not streaming")

        return StreamingResponse(
            io.BytesIO(camera.process.stdout.read()), media_type="video/mp2t"
        )

    async def stop_stream(self, camera_id: str):
        logger.info(
            f"api.services.camera_service.stop_stream: camera_id: {camera_id}, typeof(camera.process): {type(self.cameras[camera_id].process)}"
        )
        if camera_id not in self.cameras:
            raise HTTPException(status_code=404, detail="Camera not found")

        camera = self.cameras[camera_id]
        if camera.process is None:
            raise HTTPException(status_code=400, detail="Camera is not streaming")

        if camera.process is not None:
            try:
                camera.process.stdin.write("q".encode("utf-8"))
                camera.process.wait()
            except Exception as e:
                logger.error(f"Error stopping stream for camera {camera_id}: {e}")
            finally:
                camera.process = None

    async def remove_camera(self, camera_id: str):
        if camera_id not in self.cameras:
            raise HTTPException(status_code=404, detail="Camera not found")

        camera = self.cameras[camera_id]
        if camera.process is not None:
            await self.stop_stream(camera_id)

        del self.cameras[camera_id]
