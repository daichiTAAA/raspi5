from datetime import datetime

import cv2
import ffmpeg

import api.models as models
import api.schemas as schemas
from api.setup_logger import setup_logger

logger, log_decorator = setup_logger(__name__)


async def get_frame(stream: ffmpeg.Stream):
    try:
        logger.info(f"cruds.stream get_frame")
        # RTSPストリームからフレームを読み込む
        process = (
            stream.output('pipe:', format='rawvideo', pix_fmt='bgr24')
            .run_async(pipe_stdout=True, pipe_stderr=True)
        )
        frame, stderr = process.communicate()

        # ffmpegからのエラー情報をログに出力
        if stderr:
            logger.error(f"ffmpeg stderr: {stderr.decode()}")
        else:
            # フレームをJPEG形式にエンコード
            _, encoded_frame = cv2.imencode('.jpg', frame)

            return encoded_frame
    except Exception as e:
        logger.error(f"cruds.stream get_frame Error: {e}")
        raise