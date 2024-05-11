from fastapi import HTTPException
import ffmpeg
from api.models.camera import Camera

from api.setup_logger import setup_logger

logger, log_decorator = setup_logger(__name__)


class CameraService:
    def __init__(self):
        self.cameras = {}

    async def start_stream(self, camera_id: str, rtsp_url: str):
        if camera_id in self.cameras:
            raise HTTPException(status_code=400, detail="Camera is already streaming")

        try:
            process = (
                ffmpeg.input(rtsp_url, rtsp_transport="tcp")
                .output("pipe:", format="rawvideo")
                .run_async(pipe_stdout=True)
            )
            self.cameras[camera_id] = Camera(id=camera_id, process=process)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_frame(self, camera_id: str):
        logger.info("api.services.camera_service.get_frame")
        if camera_id not in self.cameras:
            return None

        camera = self.cameras[camera_id]
        frame = camera.process.stdout.read(1280 * 720 * 3)
        return frame

    async def stop_stream(self, camera_id: str):
        if camera_id not in self.cameras:
            return

        camera = self.cameras[camera_id]
        camera.process.stdin.write("q".encode("utf-8"))
        camera.process.wait()
        del self.cameras[camera_id]