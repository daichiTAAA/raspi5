from fastapi import HTTPException, WebSocket, WebSocketDisconnect

import api.models as models
from api.setup_logger import setup_logger

logger, log_decorator = setup_logger(__name__)


class UserCameraService:
    """
    UserCameraServiceクラスはシングルトンパターンを使用しています。

    理由:
    1. FFmpegプロセスの管理:
       - FFmpegプロセスはシステムリソースを消費するため、複数のインスタンスが同時に存在するとリソースの競合や過剰な消費が発生する可能性があります。
       - シングルトンパターンを使用することで、FFmpegプロセスの管理を一元化し、リソースの効率的な使用を保証します。

    2. ユーザーインスタンスの一貫性:
       - ユーザーインスタンスの追加、取得、削除などの操作を一つのインスタンスで管理することで、一貫性を保ちます。
       - 複数のインスタンスが存在すると、ユーザーインスタンスの状態が不整合になる可能性があります。

    3. ログの一元管理:
       - ログの記録を一つのインスタンスで行うことで、ログの一貫性と可読性を向上させます。
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.info("UserCameraService instance created")
        return cls._instance

    def create_usercamera_instance(
        self,
        user_id: str,
        camera_id: str,
        rtsp_url: str,
        cloud_domain: str,
        cloud_port: int,
    ):
        if models.UserCameraInstances.get_instance(user_id, camera_id):
            logger.error(
                f"Usercamera already exists: user_id: {user_id}, camera_id: {camera_id}"
            )
            raise HTTPException(status_code=400, detail="Usercamera already exists")
        wss_url = f"wss://{cloud_domain}:{cloud_port}/ws/{user_id}/{camera_id}"
        try:
            usercamera_instance = models.UserCameraInstance(
                user_id=user_id,
                camera_id=camera_id,
                rtsp_url=rtsp_url,
                wss_url=wss_url,
                wss_process=None,
                wss_stream_last_access_time=None,
            )
            models.UserCameraInstances.add_instance(
                user_id, camera_id, usercamera_instance
            )
            logger.info(
                f"Usercamera user_id {user_id}, camera_id {camera_id} added successfully"
            )
        except Exception as e:
            logger.error(
                f"Error adding usercamera user_id {user_id}, camera_id {camera_id}: {e}"
            )
            raise HTTPException(status_code=500, detail=str(e))

    def get_usercamera_instances(self):
        logger.info("api.services.user_service.get_usercamera_instances")
        return models.UserCameraInstances._instances

    def get_usercamera_instance_by_user_and_camera_id(
        self, user_id: str, camera_id: str
    ):
        logger.info(
            "api.services.usercamera_service.get_usercamera_instance_by_user_and_camera_id, user_id: {user_id}, camera_id: {camera_id}"
        )
        usercamera_instance = models.UserCameraInstances.get_instance(
            user_id, camera_id
        )
        if not usercamera_instance:
            logger.error(
                f"Usercamera not found: user_id: {user_id}, camera_id: {camera_id}"
            )
            raise HTTPException(status_code=404, detail="Usercamera not found")
        return usercamera_instance

    def delete_usercamera_instance(self, user_id: str, camera_id: str):
        usercamera_instance = models.UserCameraInstances.get_instance(
            user_id, camera_id
        )
        if not usercamera_instance:
            logger.error(
                f"Usercamera not found: user_id: {user_id}, camera_id: {camera_id}"
            )
            raise HTTPException(status_code=404, detail="Usercamera not found")

        try:
            del models.UserCameraInstances._instances[(user_id, camera_id)]
            logger.info(
                f"Usercamera user_id: {user_id}, camera_id: {camera_id} removed successfully"
            )
        except Exception as e:
            logger.error(
                f"Error removing usercamera user_id: {user_id}, camera_id: {camera_id}: {e}"
            )
            raise HTTPException(status_code=500, detail=str(e))

    async def start_wss_stream_process(
        self, websocket: WebSocket, user_id: str, camera_id: str
    ):
        """WSSストリームプロセスを開始する
        ローカルのデスクトップアプリケーションからWebSocketでビデオストリームを受信し、WebSocketsでストリームを配信する
        """
        logger.info("api.services.usercamera_service.start_wss_process")
        await websocket.accept()

        usercamera_instance = models.UserCameraInstances.get_instance(
            user_id, camera_id
        )
        if not usercamera_instance:
            logger.error(
                f"Usercamera not found: user_id: {user_id}, camera_id: {camera_id}"
            )
            raise HTTPException(status_code=404, detail="Usercamera not found")

        usercamera_instance.wss_process = None  # WebSocketプロセスを初期化

        try:
            while True:
                data = await websocket.receive_bytes()
                # 受信した動画データを処理する
                # ここでは単純に受信データをそのまま送り返す例
                await websocket.send_bytes(data)
        except WebSocketDisconnect:
            logger.info(
                f"Client disconnected: user_id: {user_id}, camera_id: {camera_id}"
            )
        except Exception as e:
            logger.error(f"Error in websocket communication: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            logger.info(
                f"Closing websocket connection: user_id: {user_id}, camera_id: {camera_id}"
            )
            usercamera_instance.wss_process = None  # WebSocketプロセスをクリア
